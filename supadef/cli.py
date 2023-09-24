import os
import subprocess
import requests
import json
import time
from typer import Typer, echo
from .credentials import parse_credentials
from tabulate import tabulate
from random import randint
from yaspin import yaspin
import zipfile


TIMEOUT_SECONDS = 3 * 60
ROOT_DOMAIN = 'https://supadef.com'
# ROOT_DOMAIN = 'http://localhost:8000'
LOCAL_CREDS_PATH = '~/.supadef/credentials.yml'


app = Typer()
# app_create = Typer()
# app.add_typer(app_create,
#               name='env',
#               no_args_is_help=True,
#               short_help="manage your project's environment variables")
#
#
# @app_create.command(name='add')
# def env_add(project: str, var: str, val: str):
#     """
#     Securely add an environment variable to your project.
#
#     All environment variables will be available in your code's runtime.
#
#     Accessible from your code via:
#     import os
#     value = os.environ['VAR_NAME']
#     :param project:
#     :param var:
#     :param val:
#     :return:
#     """
#     pass


def execute_bash_command(cmd):
    print(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd, output=stdout, stderr=stderr)
    return stdout.decode().strip()


def get_credentials():
    path = os.path.expanduser(LOCAL_CREDS_PATH)
    creds = parse_credentials(path)
    if not creds:
        raise Exception(f"Please add your credentials to {path}")
    return creds


def get_auth_headers():
    creds = get_credentials()

    uid = creds.get('uid')
    key = creds.get('api_key')

    if not uid:
        raise Exception('Please include your account ID by using the "uid" attribute')
    if not key:
        raise Exception('Please include your API Key by using the "api_key" attribute')

    headers = {
        "Authorization": f"uid:{uid} key:{key}",
    }
    return headers


def zip_directory(directory_path, zip_filename):
    # Create a ZIP file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname=arcname)


def upload_file(file_path, upload_url):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        response = requests.post(upload_url,
                                 headers=get_auth_headers(),
                                 files=files,
                                 timeout=TIMEOUT_SECONDS)
        print(response.status_code)
        print(response.json())
        if not response.status_code == 200:
            pass
        return response.json()


@app.command()
def connect():
    """check that you can securely connect to the supadef platform"""
    with yaspin(text="Connecting to supadef platform", color="yellow") as sp:
        response = requests.get(f"{ROOT_DOMAIN}/email", headers=get_auth_headers())
        sp.text = f'Connected [{response.json()}]'
        sp.ok("✅ ")
        # print(response.status_code)
        # print(response.json())


@app.command()
def create(project_name: str):
    """create a new project"""
    body = {
        'name': project_name
    }
    response = requests.post(f"{ROOT_DOMAIN}/project", headers=get_auth_headers(), json=body, timeout=TIMEOUT_SECONDS)
    print(response.status_code)
    print(response.json())


@app.command()
def push(project_name: str, path_to_code: str):
    """push your code to a project"""
    with yaspin(text=f"Pushing your code to {project_name}", color="yellow") as sp:
        try:
            upload_url = f"{ROOT_DOMAIN}/project/{project_name}/upload_package"  # Replace with your actual upload endpoint URL
            zip_filename = "package.zip"
            zip_directory(path_to_code, zip_filename)
            upload_result_json = upload_file(zip_filename, upload_url)
            sp.text = f'Uploaded your code'
            sp.ok("✅ ")
        except Exception as e:
            sp.text = 'Something went wrong'
            sp.fail()
            print(e)


@app.command(name='set_env')
def set_env(project_name: str, path_to_env_file: str):
    """Securely upload an environment file (.env) to your project"""
    with yaspin(text=f"Securely uploading your environment to project:{project_name}", color="yellow") as sp:
        try:
            upload_url = f"{ROOT_DOMAIN}/project/{project_name}/set_env"  # Replace with your actual upload endpoint URL
            upload_result_json = upload_file(path_to_env_file, upload_url)
            sp.text = f'Uploaded'
            sp.ok("✅ ")
        except Exception as e:
            sp.text = 'Something went wrong'
            sp.fail()
            print(e)


@app.command()
def run(project: str,
        function: str,
        args: str,
        version: str):
    """run your function in the cloud"""
    with yaspin(text="Submitting task...", color="yellow") as sp:
        run_url = os.path.join(ROOT_DOMAIN, 'run')

        body = {
            'project': project,
            'function': function,
            'args': args,
            'version': version
        }
        response = requests.post(run_url, headers=get_auth_headers(), json=body,
                                 timeout=TIMEOUT_SECONDS)
        print(response.status_code)
        pretty_json = json.dumps(response.json(), indent=4)
        print(pretty_json)

        if response.status_code == 200:
            sp.text = f'Task submitted'
            sp.ok("✅ ")
        else:
            sp.text = 'Something went wrong'
            sp.fail()
            print(response.status_code)
            print(response.json())


@app.command()
def logs(project: str, task_id: str):
    """
    get a function's run logs, for a particular run
    """
    with yaspin(text="Getting logs...", color="yellow") as sp:
        run_url = os.path.join(ROOT_DOMAIN, f'fn/logs/{project}/{task_id}')
        response = requests.get(run_url, headers=get_auth_headers(), timeout=TIMEOUT_SECONDS)

        if response.status_code == 200:
            sp.text = f'Got logs'
            sp.ok("✅ ")
            pretty_json = json.dumps(response.json(), indent=4)
            print(pretty_json)
        else:
            sp.text = 'Something went wrong'
            sp.fail()
            print(response.status_code)
            print(response.json())


@app.command()
def projects():
    """list your projects"""
    with yaspin(text="Getting projects", color="yellow") as sp:
        response = requests.get(f"{ROOT_DOMAIN}/projects", headers=get_auth_headers())
        __projects = response.json()

        sp.text = f'Done'
        sp.ok("✅ ")

        headers = ['state', 'name', 'created_at', 'error_msg']
        table = [[p[x] for x in headers] for p in __projects]
        echo(tabulate(table, headers=headers))


@app.command()
def destroy(project_name: str):
    """destroy a project"""
    body = {
        'name': project_name
    }
    response = requests.delete(f"{ROOT_DOMAIN}/project", headers=get_auth_headers(), json=body, timeout=TIMEOUT_SECONDS)
    print(response.status_code)
    print(response.json())


# @app.command()
# def spinner():
#     with yaspin(text="Connecting to platform", color="yellow") as spinner:
#         time.sleep(2)  # time consuming code
#         spinner.ok("✅ ")
#
#     with yaspin(text="Creating project record", color="yellow") as spinner:
#         time.sleep(2)  # time consuming code
#         spinner.ok("✅ ")
#
#     with yaspin(text="Provisioning project resources", color="yellow") as spinner:
#         time.sleep(2)  # time consuming code
#         spinner.ok("✅ ")
#
#     with yaspin(text="Deploying latest", color="yellow") as spinner:
#         time.sleep(2)  # time consuming code
#         spinner.ok("✅ ")
#
#     # with yaspin(text="Creating project record", color="yellow") as spinner:
#     #     time.sleep(2)  # time consuming code
#     #
#     #     success = randint(0, 1)
#     #     if success:
#     #         spinner.ok("✅ ")
#     #     else:
#     #         spinner.fail("💥 ")


if __name__ == "__main__":
    app()

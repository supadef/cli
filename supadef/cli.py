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


def execute_bash_command(cmd):
    print(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd, output=stdout, stderr=stderr)
    return stdout.decode().strip()


def get_auth_headers():
    default_path = '~/.supadef/credentials.yml'
    path = os.path.expanduser(default_path)
    creds = parse_credentials(path)

    if not creds:
        raise Exception(f"Please add your credentials to {path}")

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


app = Typer()


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
    def zip_directory(directory_path, zip_filename):
        # Create a ZIP file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, directory_path)
                    zipf.write(file_path, arcname=arcname)

    def upload_zip_file(zip_filename, upload_url):
        with open(zip_filename, 'rb') as file:
            files = {'file': (zip_filename, file)}
            body = {
                'name': project_name
            }
            response = requests.post(upload_url,
                                     headers=get_auth_headers(),
                                     # json=body,
                                     files=files,
                                     timeout=TIMEOUT_SECONDS)
            print(response.status_code)
            print(response.json())

    upload_url = f"{ROOT_DOMAIN}/project/{project_name}/upload_package"  # Replace with your actual upload endpoint URL
    zip_filename = "package.zip"
    zip_directory(path_to_code, zip_filename)
    upload_zip_file(zip_filename, upload_url)


@app.command()
def run(project: str,
        function: str,
        args: str,
        version: str):
    """run your function in the cloud"""
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

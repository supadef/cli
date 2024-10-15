from typing import List
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from enum import Enum
import os
import subprocess
import sys
import requests
import json
import time
import traceback
from typer import Typer, echo
import typer

from .config import TIMEOUT_SECONDS, SERVICE_ENDPOINT, LOCAL_CREDS_PATH
from .credentials import parse_credentials
from .links import link
# TODO: figure out a way to centralize version
# from ..version import VERSION
from tabulate import tabulate
from random import randint
from yaspin import yaspin
import zipfile
import os
import tempfile
import shutil


app = Typer()


def execute_bash_command(cmd):
    print(cmd)
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode, cmd, output=stdout, stderr=stderr)
    return stdout.decode().strip()


def get_credentials():
    path = os.path.expanduser(LOCAL_CREDS_PATH)
    creds = parse_credentials(path)
    if not creds:
        raise Exception(f"Please add your credentials to {path}")
    return creds


def get_auth_headers():
    creds = get_credentials()

    api_key_id = creds.get('api_key_id')
    api_key = creds.get('api_key')

    if not api_key_id:
        raise Exception(
            'Please include your API Key ID by using the "api_key_id" attribute')
    if not api_key:
        raise Exception(
            'Please include your API Key by using the "api_key" attribute')

    headers = {
        "Authorization": f"api_key_id:{api_key_id} api_key:{api_key}",
    }
    return headers


def create_tempdir(key, nuke_existing=True):
    """
    Create a clean temporary directory.
    """
    # get the path that we should do our work in
    cwd = os.path.join(tempfile.gettempdir(), 'com.supadef.tempdir', key)
    # nuke the working directory, if it exists
    if nuke_existing and os.path.exists(cwd):
        # https://stackoverflow.com/questions/6996603/how-can-i-delete-a-file-or-folder-in-python
        shutil.rmtree(cwd)
    # create it
    os.makedirs(cwd)
    return cwd


def zip_directory(directory_path, zip_filename):
    # Create a ZIP file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname=arcname)


def zip_directory_in_isolated_tempdir(path_to_code: str) -> str:
    # create an isolated directory to build the package
    work_dir = create_tempdir('supadef_packages')
    # copy tree only works on non-existent directories :/
    shutil.rmtree(work_dir)
    # copy the source code to the build directory
    shutil.copytree(path_to_code, work_dir)
    # wire up the full path to the package.zip file
    zip_filename = "package.zip"
    path_to_package_zip = os.path.join(work_dir, zip_filename)
    # zip up the code in the working dir, which has the client code. place output in that dir
    zip_directory(work_dir, path_to_package_zip)
    return path_to_package_zip


def zip_directory_in_isolated_tempdir_v2(path_to_code: str) -> str:
    # create an isolated directory to build the package
    work_dir = create_tempdir('supadef_packages')

    def read_gitignore():
        gitignore_path = os.path.join(path_to_code, '.gitignore')

        # Check if .gitignore file exists
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as file:
                content = file.read()
            return content
        return ''

    # pull down the default .sd_ignore
    default_sd_ignore = GET_TEXT('/defaults/.sd_ignore')
    # read in the user's .gitignore
    user_git_ignore = read_gitignore()

    copy_dir(path_to_code, work_dir, default_sd_ignore + '\n' + user_git_ignore)

    # wire up the full path to the package.zip file
    zip_filename = "package.zip"
    path_to_package_zip = os.path.join(work_dir, zip_filename)
    # zip up the code in the working dir, which has the client code. place output in that dir
    zip_directory(work_dir, path_to_package_zip)
    return path_to_package_zip


def upload_file(file_path, upload_url):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        response = requests.post(upload_url,
                                 headers=get_auth_headers(),
                                 files=files,
                                 timeout=TIMEOUT_SECONDS)
        json = response.json()
        if not response.status_code == 200:
            error_msg = json['detail']
            raise ValueError(error_msg)
        return json


class FailMode(Enum):
    EXIT = 1
    THROW_ERROR = 2


def serialize_exception(exception):
    return {
        'type': type(exception).__name__,
        'message': str(exception),
        # 'args': exception.args,
        'traceback': ''.join(traceback.format_exception(None, exception, exception.__traceback__))
    }


def run_step(step_name: str, f: callable, fail_mode: FailMode = FailMode.EXIT):
    """
    Run a given step, defined in the function f.

    To make it possible for the function f to 'print' outputs, it must be of the form:

    f(sp: Yaspin)

    then, you can 'print' outputs with:

    sp.write(___)
    """
    with yaspin(text=f"Running: [{step_name}]", color="yellow") as sp:
        try:
            out = f(sp)
            sp.text = ''
            sp.ok(f"Done ✅: [{step_name}]")
            return out
        except Exception as e:
            sp.text = str(e)
            sp.fail(f"Error ❌: [{step_name}]")
            if fail_mode == FailMode.EXIT:
                exit()
            if fail_mode == FailMode.THROW_ERROR:
                raise e


def GET(route: str, params: dict = None, debug=False) -> dict:
    response = requests.get(f'{SERVICE_ENDPOINT}{route}',
                            headers=get_auth_headers(),
                            timeout=TIMEOUT_SECONDS,
                            params=params)
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json


def GET_TEXT(route: str) -> dict:
    response = requests.get(f'{SERVICE_ENDPOINT}{route}')
    t = response.text
    if not response.status_code == 200:
        raise ValueError(t)
    return t


def POST(route: str, body: dict, handle_error=None) -> dict:
    response = requests.post(f'{SERVICE_ENDPOINT}{route}',
                             headers=get_auth_headers(),
                             timeout=TIMEOUT_SECONDS,
                             json=body)
    json = response.json()
    if not response.status_code == 200:
        error_msg = json['detail']
        raise ValueError(error_msg)
    return json


@app.command()
def connect():
    """check that you can securely connect to the supadef platform"""
    with yaspin(text="Connecting to supadef platform", color="yellow") as sp:
        json = GET('/cli/connect')
        sp.text = f'Connected [{json}]'
        sp.ok("✅ ")


@app.command()
def create(project_name: str):
    """create a new project"""

    with yaspin(text="Creating project", color="yellow") as sp:
        json = POST('/projects/create', {
            'name': project_name
        })
        sp.text = f"Project created: '{project_name}'"
        sp.ok("✅ ")


@app.command()
def projects():
    """list your projects"""
    with yaspin(text="Getting projects", color="yellow") as sp:
        json = GET('/projects/json')

        sp.text = f'Done'
        sp.ok("✅ ")

        headers = ['name', 'created_at']
        table = [[p[x] for x in headers] for p in json]
        echo(tabulate(table, headers=headers))


def get_non_ignored_files(directory: str, gitignore_content: str) -> List[str]:
    # Create a PathSpec object from the gitignore content
    spec = PathSpec.from_lines(
        GitWildMatchPattern, gitignore_content.splitlines())

    non_ignored_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(
                os.path.join(root, file), directory)
            if not spec.match_file(file_path):
                non_ignored_files.append(file_path)

    return non_ignored_files


def copy_dir(source_dir: str, dest_dir: str, gitignore_content: str):
    def get_non_ignored_files(directory: str, gitignore_content: str) -> List[str]:
        # Create a PathSpec object from the gitignore content
        spec = PathSpec.from_lines(
            GitWildMatchPattern, gitignore_content.splitlines())

        non_ignored_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.relpath(
                    os.path.join(root, file), directory)
                if not spec.match_file(file_path):
                    non_ignored_files.append(file_path)

        return non_ignored_files

    # Get the list of files to copy
    files_to_copy = get_non_ignored_files(source_dir, gitignore_content)

    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Copy each non-ignored file
    for file_path in files_to_copy:
        source_file = os.path.join(source_dir, file_path)
        dest_file = os.path.join(dest_dir, file_path)

        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)

        # Copy the file
        shutil.copy2(source_file, dest_file)
        print(f"Copied: {file_path}")

    print(f"Copied {len(files_to_copy)} files from {source_dir} to {dest_dir}")


@app.command(name='sd_ignore')
def sd_ignore():
    """View the default .sd_ignore file (.gitignore style - exclude files from supadef build)"""
    with yaspin(text="Getting default .sd_ignore file", color="yellow") as sp:
        t = GET_TEXT('/defaults/.sd_ignore')

        sp.text = f'Done'
        sp.ok("✅ ")
        echo(t)


@app.command()
def push(project_name: str, path_to_code: str, debug: bool = typer.Option(False, "--debug", help="Enable debug mode")):
    """push your code to a project"""

    def __log_debug(msg, sp=None):
        """
        log a message when the --debug flag is enabled
        """
        if debug:
            # if using Yaspin:
            if sp:
                sp.write(msg)
            else:
                # otherwise, default way to write Typer outputs
                echo(msg)

    def step1_zip(sp):
        __log_debug(f'path_to_code: {path_to_code}', sp)
        path_to_zip = zip_directory_in_isolated_tempdir_v2(
            path_to_code)
        __log_debug(f'path_to_zip: {path_to_zip}', sp)
        filename = os.path.basename(path_to_zip)
        return path_to_zip, filename

    path_to_zip, filename = run_step('Package code as .zip', step1_zip)

    # print(f'Package: {path_to_zip}')

    def step2_get_upload_url(sp):
        r = GET('/cli/get_upload_zip_presigned_url',
                params={'project_name': project_name, 'file_name': filename})
        __log_debug(f"GET('/cli/get_upload_zip_presigned_url') -> {r}", sp)
        if not 'url' in r:
            raise ValueError('Could not get upload URL - missing url')
        if not 'fields' in r:
            raise ValueError('Could not get upload URL - missing fields')
        return r

    presigned_post_data = run_step('Get upload URL', step2_get_upload_url)

    # print(f'presigned_post_data: {presigned_post_data}')

    # print('-------')
    # print(f"url: {presigned_post_data['url']}")
    # print(f"fields: {presigned_post_data['fields']}")
    # print(f"fields.key: {presigned_post_data['fields']['key']}")
    # print('-------')

    # def step3_upload_zip(sp):
    #     with open(path_to_zip, 'rb') as file:
    #         files = {'file': (presigned_post_data['fields']['key'], file)}
    #         response = requests.post(
    #             presigned_post_data['url'], data=presigned_post_data['fields'], files=files)

    #     if not (response and response.status_code == 204):
    #         raise ValueError(
    #             f"Failed to upload file: {response.status_code} - {response.text}")

    def step3_upload_zip(sp):
        def upload_file_with_redirect_handling(url, fields, file_path):
            max_retries = 3  # Number of retries
            for attempt in range(max_retries):
                try:
                    # Open the file to upload
                    with open(file_path, 'rb') as file:
                        __log_debug(f'[start] POST: {url}', sp)
                        response = requests.post(
                            url,
                            data=fields,
                            files={'file': (fields['key'], file)},
                            allow_redirects=False,  # Disable automatic redirect handling
                        )
                        __log_debug(f'[response] POST: {url} | {response}', sp)

                    # Check if a redirect is needed
                    if response.status_code in [301, 302]:
                        redirect_url = response.headers.get('Location')
                        if redirect_url:
                            __log_debug(f"Redirecting to: {redirect_url}", sp)
                            # Retry the upload at the new endpoint
                            url = redirect_url
                            continue
                        else:
                            raise ValueError(
                                'Redirect location not provided in response')
                    else:
                        # If no redirect is needed or request is successful, break the loop
                        response.raise_for_status()
                        return response

                except requests.RequestException as e:
                    __log_debug(f"Redirecting to: {redirect_url}", sp)
                    if attempt < max_retries - 1:
                        __log_debug("Retrying...", sp)
                    else:
                        raise  # Re-raise the exception if max retries exceeded

        upload_file_with_redirect_handling(
            presigned_post_data['url'], presigned_post_data['fields'], path_to_zip)

        # with open(path_to_zip, 'rb') as file:
        #     files = {'file': (presigned_post_data['fields']['key'], file)}
        #     response = requests.post(
        #         presigned_post_data['url'], data=presigned_post_data['fields'], files=files)

        # if not (response and response.status_code == 204):
        #     raise ValueError(
        #         f"Failed to upload file: {response.status_code} - {response.text}")

    try:
        upload_response = run_step(
            f'Upload package to project:{project_name}', step3_upload_zip, fail_mode=FailMode.THROW_ERROR)

        json = POST('/cli/finish_zip_upload', {
            'name': project_name,
            'status': 'success'
        })
    except Exception as e:
        json = POST('/cli/finish_zip_upload', {
            'name': project_name,
            'status': 'error',
            'error': serialize_exception(e)
        })


@ app.command(name='set_env')
def set_env(project_name: str, path_to_env_file: str):
    """Securely upload an environment file (.env) to your project"""
    with yaspin(text=f"Securely uploading your environment to project:{project_name}", color="yellow") as sp:
        try:
            upload_url = link('supadef set_env', project=project_name)
            upload_result_json = upload_file(path_to_env_file, upload_url)
            sp.text = f'Uploaded'
            sp.ok("✅ ")
        except Exception as e:
            sp.text = 'Something went wrong'
            sp.fail()
            print(e)


@ app.command()
def run(project: str,
        function: str,
        args: str,
        version: str):
    """run your function in the cloud"""
    with yaspin(text="Submitting task...", color="yellow") as sp:
        try:
            run_url = link('supadef run')

            body = {
                'project': project,
                'function': function,
                'args': args,
                'version': version
            }
            response = requests.post(run_url, headers=get_auth_headers(), json=body,
                                     timeout=TIMEOUT_SECONDS)

            j = response.json()
            if not response.status_code == 200:
                error_msg = j['detail']
                raise ValueError(error_msg)

            sp.text = f'Task submitted'
            sp.ok("✅ ")
            pretty_json = json.dumps(j, indent=4)
            print(pretty_json)
        except Exception as e:
            sp.text = str(e)
            sp.fail("❌ ")


@ app.command()
def logs(run_id: str):
    """
    get a function's run logs, for a particular run
    """
    with yaspin(text="Getting logs...", color="yellow") as sp:
        run_url = link('supadef logs', run_id=run_id)
        response = requests.get(
            run_url, headers=get_auth_headers(), timeout=TIMEOUT_SECONDS)

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


@ app.command()
def destroy(project_name: str):
    """destroy a project"""
    body = {
        'name': project_name
    }
    response = requests.delete(link('supadef destroy'), headers=get_auth_headers(
    ), json=body, timeout=TIMEOUT_SECONDS)
    print(response.status_code)
    print(response.json())


@ app.command()
def about():
    """basic info about the running version of the CLI"""
    # print(f'Version: {VERSION}')
    print(f'Service endpoint: {SERVICE_ENDPOINT}')
    print(f'Looking for credentials at: {LOCAL_CREDS_PATH}')


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

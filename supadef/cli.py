import os
import subprocess
import requests
from typer import Typer
from .credentials import parse_credentials


TIMEOUT_SECONDS = 3 * 60


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
        "Content-Type": "application/json"
    }
    return headers


app = Typer()


@app.command()
def connect():
    """check that you can securely connect to the supadef platform"""
    response = requests.get("https://supadef.com/email", headers=get_auth_headers())
    print(response.status_code)
    print(response.json())


@app.command()
def create(project_name: str):
    """create a new project"""
    # 1.
    execute_bash_command(f'mkdir -p {project_name}')
    execute_bash_command(f'touch {project_name}/supadef.yml')
    body = {
        'name': project_name
    }
    response = requests.post("https://supadef.com/project", headers=get_auth_headers(), json=body, timeout=TIMEOUT_SECONDS)
    print(response.status_code)
    print(response.json())


@app.command()
def destroy(project_name: str):
    """destroy a project"""
    body = {
        'name': project_name
    }
    response = requests.delete("https://supadef.com/project", headers=get_auth_headers(), json=body, timeout=TIMEOUT_SECONDS)
    print(response.status_code)
    print(response.json())


@app.command()
def projects():
    """list your projects"""
    response = requests.get("https://supadef.com/projects", headers=get_auth_headers())
    print(response.status_code)
    print(response.json())


@app.command()
def push():
    print('push')
    pass



if __name__ == "__main__":
    app()

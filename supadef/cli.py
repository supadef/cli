from supadef.platform import run_server_task
from supadef.util import run_step
from .version import VERSION
from .push import push_project, set_project_env
import subprocess
import json
import requests
from typer import Typer, echo
import typer
from .config import TIMEOUT_SECONDS, SERVICE_ENDPOINT, LOCAL_CREDS_PATH
from tabulate import tabulate
from yaspin import yaspin
from .network import GET, POST, get_auth_headers, GET_TEXT

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
    push_project(project_name, path_to_code, debug)


@app.command(name='set_env')
def set_env(project_name: str, path_to_env_file: str, debug: bool = typer.Option(False, "--debug", help="Enable debug mode")):
    """Securely upload an environment file (.env) to your project"""
    set_project_env(project_name, path_to_env_file, debug)


@app.command(name='run_server_task')
def _run_server_task(project: str,
                     function: str,
                     args: str):
    """run your function in the cloud"""

    args_dict = json.loads(args)

    def run_it(log):
        run_server_task(project, function, args_dict)

    result = run_step(f'[@server_task] run {function}', run_it)
    return result


@app.command()
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


@app.command()
def destroy(project_name: str):
    """destroy a project"""
    body = {
        'name': project_name
    }
    response = requests.delete(link('supadef destroy'), headers=get_auth_headers(
    ), json=body, timeout=TIMEOUT_SECONDS)
    print(response.status_code)
    print(response.json())


@app.command()
def about():
    """basic info about the running version of the CLI"""
    print(f'v{VERSION}')
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

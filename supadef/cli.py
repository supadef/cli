import subprocess
import requests
from typer import Typer


def execute_bash_command(cmd):
    print(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd, output=stdout, stderr=stderr)
    return stdout.decode().strip()


app = Typer()


@app.command()
def hello():
    print("Hello.")


@app.command()
def bye(name: str):
    print(f"Bye {name}")


@app.command()
def init(project_name: str):
    # 1.
    execute_bash_command(f'mkdir -p {project_name}')
    execute_bash_command(f'touch {project_name}/supadef.yml')


@app.command()
def push():
    print('push')
    pass


@app.command()
def connect():
    uid = 'my_uid'
    key = 'my_key'
    headers = {
        "Authorization": f"uid:{uid} key:{key}",
        "Content-Type": "application/json"
    }

    # response = requests.get("http://localhost:8000/email", headers=headers)
    response = requests.get("https://supadef.com/email", headers=headers)

    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    app()
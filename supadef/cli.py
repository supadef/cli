import subprocess
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
    execute_bash_command(f'')


@app.command()
def push():
    print('push')
    pass


if __name__ == "__main__":
    app()

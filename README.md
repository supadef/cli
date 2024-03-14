# Supadef PyPi Package / CLI

# Overview
The ```supadef``` python package lets you define how your Python functions run in the cloud using decorators like ```@task```.

The ```supadef``` CLI tool allows you to interact with the Supadef platform.
You can use it to manage projects, functions, and deployments. 

[//]: # (You can use it to create, deploy, list, and destroy projects.)

# Commands

<!-- ```bash
supadef login
```
* Log in to the platform with email and password. 
Upon successful login, saves your API Key and account ID to ```~/.supadef/credentials.yml```.
This lets the CLI make authenticated calls on your behalf. -->
```bash
supadef connect
```
* Make a test connection with the platform. Verifies that your auth credentials saved at ```~/.supadef/credentials.yml``` are configured correctly. Returns the email of the authenticated user.
```bash
supadef create [project]
```
* Create a new project with the given name in your account.
Project names must be unique across all Supadef projects.
<!-- Must be run from a git repository.  -->
<!-- Adds a new git remote called ```supadef``` to the local repo. -->

```bash
supadef projects
```
* List the projects in your account. Includes information on your project's deployment state.


```bash
supadef push [project] [path/to/code_dir]
```
* Push the source code you specify to the cloud. Appropriately configured functions will be available to run on demand in the cloud. Source code directory must be a git repo. Anything in .gitignore will not be uploaded.

```bash
supadef run [project] 'your_function' '{ "arg1":  "drums", "arg2": [1, 2, 3, 4] }' [version]
```
* Run a function in the cloud. [version] will soon be optional, or removed, to simplify the interface. Returns a task_id, for use with getting logs.
```bash
supadef logs [project] [task_id]
```
* Get the logs for a particular function run.
```bash
supadef set_env [project] [~/path/to/.env]
```
* Securely upload an environment file (.env) to your project

<!-- ```bash
supadef deploy [env] [commit]
```
* Deploy your project.
You can set the version, and environment if you want. -->

```bash
supadef destroy [project]
```
* Destroy a project and all resources associated with it.
<!-- ```bash
supadef open [project]
```
* Open your project in the system web browser. -->


# Distribution

PyPI Package: [https://pypi.org/project/supadef/](https://pypi.org/project/supadef/)

Github Repo: https://github.com/supadef/cli


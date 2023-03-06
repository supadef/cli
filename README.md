# Supadef CLI ⚡️
_Official command-line interface to the Supadef platform._

## Overview
The ```supadef``` CLI tool allows you to interact with the Supadef platform.
You can use it to manage projects, functions, and deployments. 

[//]: # (You can use it to create, deploy, list, and destroy projects.)

## Commands

```bash
supadef login
```
* Log in to the platform with email and password. 
Upon successful login, saves your API Key and account ID to ```~/.supadef/credentials.yml```.
This lets the CLI make authenticated calls on your behalf.
```bash
supadef connect
```
* Make a test connection with the platform. Verifies that your auth credentials saved at ```~/.supadef/credentials.yml``` are configured correctly. Returns the email of the authenticated user.
```bash
supadef create [project]
```
* Create a new project with the given name in your account.
Project names must be unique across all Supadef projects.
Must be run from a git repository. 
Adds a new git remote called ```supadef``` to the local repo.
```bash
supadef deploy [env] [commit]
```
* Deploy you project.
You can set the version, and environment if you want.

```bash
supadef projects
```
* List the projects in your account. Includes information on your project's deployment state.
```bash
supadef destroy [project]
```
* Destroy a project and all resources associated with it.
```bash
supadef logs
```
* Stream your project's logs.
```bash
supadef open [project]
```
* Open your project in the system web browser.

## Tutorials


## Distribution

Distributed via PyPI package: [https://pypi.org/project/supadef/](https://pypi.org/project/supadef/)

Open Source Github Repo: https://github.com/supadef/cli


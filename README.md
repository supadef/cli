# Supadef CLI ⚡️
_Official command-line interface to the Supadef platform._

## Overview
The ```supadef``` CLI tool allows you to interact with the Supadef platform.
You can use it to create, deploy, list, and destroy projects.

## Commands

```bash
supadef login
```
* Log in to the platform with email/password.
```bash
supadef create [project]
```
* Create a new project with the given name in your account. Project names must be unique across all Supadef projects.
```bash
supadef deploy [env] [commit]
```
* Deploy you project. You can set the version, and environment if you want.

```bash
supadef projects
```
* List the projects in your account. Will include information on your project's deployment state.
```bash
supadef destroy [project]
```
* Destroy a project and all resources associated with it.
```bash
supadef logs
```
* Stream your project's logs.

## Distribution

Distributed via PyPI package: [https://pypi.org/project/supadef/](https://pypi.org/project/supadef/)

Open Source Github Repo: https://github.com/supadef/cli


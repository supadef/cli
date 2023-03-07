# Supadef CLI ⚡️
_Official command-line interface to the Supadef platform._

# Overview
The ```supadef``` CLI tool allows you to interact with the Supadef platform.
You can use it to manage projects, functions, and deployments. 

[//]: # (You can use it to create, deploy, list, and destroy projects.)

# Commands

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
* Deploy your project.
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

# Decorators
The main magic behind Supadef is the fact that you can deploy
full-stack apps with just a few lines of Python.

Tell Supadef how you want to deploy your functions by using decorators.

[//]: # (Deploy apps, endpoints, workers, web-forms)

## Example: Hello world!
Must keep with tradition 🤪

This example builds a simple app that takes a name, and says hello to that name :)

Decorators used:```@compose```, ```@text_input```, ```@button```, ```@card```

```python
from supadef import compose, text_input, button, card

@compose(
    text_input('name'),
    button('Hello'),
    returns=card
)
def hello_world(name: str):
    return f'Hello, {name}'
```


## Example: A sign-up form

Decorators used:
```@compose```,
```@text_input```, 
```@button```, 
```@card```, 
```@subtitle```, 

```python
from supadef import compose, text_input, button, card, title

@compose(
    text_input('name'),
    text_input('email'),
    text_input('password', hidden=True),
    button('Sign Up'),
    returns=(
        card('out0'),
        title('h3', 'out1')
    )
)
def sign_up(name: str,
            email: str, 
            password: str):
    
    # Authenticate with Auth provider here
    
    return (
        f'Welcome back, {name}!',
        f'In case you forgot, your email is: {email}'
    )
```

## Example: An auth-protected HTTP endpoint, along with client SDKs in Swift & Javascript
Decorators used: ```@endpoint```, ```@sdk```, ```@auth```
```python
from supadef import endpoint, sdk, auth

@endpoint('GET /recommendations') # Scalable Web API
@sdk('swift') # auto-generate networking code & simple Swift View Controllers
@sdk('javascript') # auto-generate networking code & simple HTML/CSS Forms
@auth('user_id') # must be logged in to run this function.
def get_video_recommendations(user_id: str):
    videos = []
    
    # Run your ML model here

    return videos
```

## Example: Get a Ride feature in a ride-share app
Decorators used: ```@map_selector```, 
```@auth```, 
```@compose```,
```@map_view```, 
```@drawer```,
```@vstack```,
```@options```,
```@button```,
```@goto```,
```python
from supadef import map_selector, auth
from supadef.data import Address


@auth('user_id') # must be logged in to run this function.
@map_selector('address') # gives a nice UX for selecting an address, complete with a Map View
@goto('choose_ride_level')
def select_desination(user_id: str, address: Address):
    return address


@auth('user_id') # must be logged in to run this function.
@compose( # let's us define endlessly customizable UI layout
    map_view('address'), # display a full-page map view.
    drawer( # UI component that slides out
        vstack(
            options('level',[
                'Uber X',
                'Uber Black',
                'Uber XL',
                'Uber Pool',
            ]),
            button('Confirm Ride')      
        )
    ),
)
def choose_ride_level(address: Address, level: str):
    pass
```



# Tutorials
[todo]

# Distribution

Distributed via PyPI package: [https://pypi.org/project/supadef/](https://pypi.org/project/supadef/)

Open Source Github Repo: https://github.com/supadef/cli


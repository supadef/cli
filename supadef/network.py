import os
import orjson
import requests
from .config import SERVICE_ENDPOINT, LOCAL_CREDS_PATH, TIMEOUT_SECONDS
from .credentials import parse_credentials


def get_credentials():
    path = os.path.expanduser(LOCAL_CREDS_PATH)
    creds = parse_credentials(path)
    if not creds:
        raise Exception(f"Please add your credentials to {path}")
    return creds


def get_auth_headers():
    creds = get_credentials()
    api_key = creds.get('default')

    if not api_key:
        raise Exception(
            'Please include your API Key by using the "default" attribute. Only the default key is supported, for now.')

    headers = {
        "Authorization": f"{api_key}",
        "Content-Type": "application/json"
    }
    return headers


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


def POST(route: str, body: dict, handle_error=None) -> dict:
    response = requests.post(f'{SERVICE_ENDPOINT}{route}',
                             headers=get_auth_headers(),
                             timeout=TIMEOUT_SECONDS,
                             data=orjson.dumps(body))
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

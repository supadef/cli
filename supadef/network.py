import orjson
import requests

from supadef.credentials import get_api_key
from .config import SERVICE_ENDPOINT, TIMEOUT_SECONDS


def get_auth_headers():
    api_key = get_api_key(profile=None)

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

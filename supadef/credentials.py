import os
from typing import Optional
import yaml

from supadef.config import LOCAL_CREDS_PATH


def parse_credentials(path):
    text = open(path).read()
    creds = yaml.safe_load(text)
    return creds


def get_api_key(profile: Optional[str] = None):
    # if an env variable has been explicitly set, use that
    SUPADEF_API_KEY = os.getenv("SUPADEF_API_KEY", None)
    if SUPADEF_API_KEY:
        return SUPADEF_API_KEY
    # read ~/.supadef/credentials.yml
    path = os.path.expanduser(LOCAL_CREDS_PATH)
    creds = parse_credentials(path)
    if not creds:
        raise Exception(f"Please add your credentials to {path}")
    if profile:
        profile_api_key = creds.get(profile)
        if profile_api_key:
            return profile_api_key
        raise ValueError(f"No profile named '{profile}'")

    api_key = creds.get('default')

    if not api_key:
        raise ValueError(
            'Please include your API Key by using the "default" attribute. Only the default key is supported, for now.')

    return api_key

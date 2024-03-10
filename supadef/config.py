import os

TIMEOUT_SECONDS = 3 * 60
SERVICE_ENDPOINT = 'https://supadef.com'
if 'SUPADEF_SERVICE_ENDPOINT' in os.environ:
    # SERVICE_ENDPOINT = 'http://localhost:8000'
    SERVICE_ENDPOINT = os.environ['SUPADEF_SERVICE_ENDPOINT']

LOCAL_CREDS_PATH = '~/.supadef/credentials.yml'

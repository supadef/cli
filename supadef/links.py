from .config import SERVICE_ENDPOINT

SLUG_TO_PATTERN = {
    'user': '/{username}',
    'user > billing': '/{username}/billing',
    'user > account': '/{username}/account',
    'user > project': '/{username}/{project}',
    'user > project > functions > run': '/{username}/{project}/{function}/{run_id}',
    'user > project > danger zone': '/{username}/{project}/danger_zone',
    'user > project > env': '/{username}/{project}/env',
    'docs > cli > supadef connect': '',
    'site > waitlist': '/get_api_key',
    'supadef connect': '/email',
    'supadef projects': '/projects',
    'supadef create': '/project',
    'supadef logs': '/fn/logs/{run_id}',
    'supadef push': '/project/{project}/upload_package',
    'supadef run': '/run',
    'supadef destroy': '/project',
    'supadef set_env': '/project/{project}/set_env'
}


# this is silly? yagni? or nah?
# perhaps if it's constrained to routes for user-specific data
# strictly GET requests (or ws 'GET's). no other operations encoded here
def route(slug: str, loader=False) -> str:
    if slug not in SLUG_TO_PATTERN.keys():
        raise ValueError(f'no such slug: {slug}')

    pattern = SLUG_TO_PATTERN[slug]
    if loader:
        pattern = pattern + '/content_html'

    return pattern


def link(slug: str,
         loader=False,
         username: str = None,
         project: str = None,
         function: str = None,
         run_id: str = None,
         service_endpoint: str = SERVICE_ENDPOINT) -> str:
    subs = {
        'username': username,
        'project': project,
        'function': function,
        'run_id': run_id
    }
    pattern = route(slug, loader).format(**subs)

    return service_endpoint + pattern

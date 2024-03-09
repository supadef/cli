from .config import SERVICE_ENDPOINT


# this is silly? yagni? or nah?
# perhaps if it's constrained to routes for user-specific data
# strictly GET requests (or ws 'GET's). no other operations encoded here
def route(slug: str, loader=False) -> str:
    slug_to_pattern = {
        'user': '/{username}',
        'user > billing': '/{username}/billing',
        'user > account': '/{username}/account',
        'user > project > functions > run': '/fn/run/{run_id}',
        'user > project > danger zone': '/{username}/{project}/danger_zone',
        'user > project > env': '/{username}/{project}/env',
        'docs > cli > supadef connect': '',
        'supadef connect': ''
    }
    if slug not in slug_to_pattern.keys():
        raise ValueError(f'no such slug: {slug}')

    pattern = slug_to_pattern[slug]
    if loader:
        pattern = pattern + '/content_html'

    return pattern


def link(slug: str,
         loader=False,
         username: str = None,
         project_name: str = None,
         service_endpoint: str = SERVICE_ENDPOINT) -> str:
    subs = {
        'username': username,
        'project_name': project_name
    }
    pattern = route(slug, loader).format(**subs)

    return service_endpoint + pattern


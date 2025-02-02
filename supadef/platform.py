from typing import Optional

from supadef.network import POST


def run_server_task(project_name: str, func_name: str, args: dict, module: Optional[str] = None):
    json = POST(f'/run/server_task', {
        'project_name': project_name,
        'func_name': func_name,
        'args': args,
        'module': module
    })
    return json

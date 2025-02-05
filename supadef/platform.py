from typing import Callable, Optional, Union

from supadef.network import POST


def run_server_task(project_name: str, func: Union[str, Callable], args: dict, module: Optional[str] = None):
    func_name = func
    if callable(func):
        func_name = func.__name__

    json = POST(f'/run/server_task', {
        'project_name': project_name,
        'func_name': func_name,
        'args': args,
        'module': module
    })
    return json

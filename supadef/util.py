from enum import Enum
import traceback
from yaspin import yaspin

class FailMode(Enum):
    EXIT = 1
    THROW_ERROR = 2

def serialize_exception(exception):
    return {
        'type': type(exception).__name__,
        'message': str(exception),
        'traceback': ''.join(traceback.format_exception(None, exception, exception.__traceback__))
    }

def run_step(step_name: str, f: callable, fail_mode: FailMode = FailMode.EXIT):
    """
    Run a given step, defined in the function f.

    To make it possible for the function f to 'print' outputs, it must be of the form:

    f(sp: Yaspin)

    then, you can 'print' outputs with:

    sp.write(___)
    """
    with yaspin(text=f"Running: [{step_name}]", color="yellow") as sp:
        try:
            out = f(sp)
            sp.text = ''
            sp.ok(f"Done ✅: [{step_name}]")
            return out
        except Exception as e:
            sp.text = str(e)
            sp.fail(f"Error ❌: [{step_name}]")
            if fail_mode == FailMode.EXIT:
                exit()
            if fail_mode == FailMode.THROW_ERROR:
                raise e

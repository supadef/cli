from rich.live import Live
from rich.spinner import Spinner
from rich.console import Console
from enum import Enum
import traceback

console = Console()


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

    f(log: callable)

    then, you can log outputs with

    log('your message')
    """

    spinner = Spinner("dots", text=f"Running: [{step_name}]", style="yellow")

    with Live(spinner, refresh_per_second=10, console=console) as live:
        def sp_write(msg):
            console.log(msg)

        try:
            out = f(sp_write)
            # Update spinner to show completion
            spinner.text = f"Done ✅: [{step_name}]"
            spinner.style = "green"
            live.update(spinner)  # Force final render
            return out
        except Exception as e:
            # Update spinner to show error
            spinner.text = f"Error ❌: [{step_name}]"
            spinner.style = "red"
            live.update(spinner)  # Force final render
            if fail_mode == FailMode.EXIT:
                console.print(f"[bold red]Fatal Error:[/bold red] {e}")
                exit(1)
            if fail_mode == FailMode.THROW_ERROR:
                raise e

# ui_components.py
from functools import wraps
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

# Import the shared console instance
from .console import console

def with_spinner(text: str):
    """
    A decorator to show a spinner for the duration of a function call.

    Args:
        text (str): The text to display next to the spinner.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with console.status(f"[bold green]{text}", spinner="dots"):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def with_progress_bar(description: str):
    """
    A decorator that provides a Rich Progress object to the decorated function.

    The decorated function MUST accept a 'progress' keyword argument.
    It is responsible for adding a task and updating the progress.

    Args:
        description (str): The initial description for the progress bar task.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
                transient=True,
            ) as progress:
                kwargs['progress'] = progress
                kwargs['description'] = description
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

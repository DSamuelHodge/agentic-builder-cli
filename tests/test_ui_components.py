import time
from restack_gen.utils.ui_components import with_spinner, with_progress_bar
from restack_gen.utils.console import console


# Test function for spinner
def test_with_spinner_decorator(capsys):
    @with_spinner("Testing spinner...")
    def dummy_task():
        time.sleep(0.1)
        console.print("[bold green]Task done![/bold green]")
        return 42

    result = dummy_task()
    assert result == 42
    captured = capsys.readouterr()
    # The spinner output is handled by Rich, but our print should be present
    assert "Task done!" in captured.out


# Test function for progress bar
def test_with_progress_bar_decorator(capsys):
    @with_progress_bar(description="[cyan]Testing progress bar...")
    def dummy_progress_task(n, *, progress, description):
        task = progress.add_task(description, total=n)
        for i in range(n):
            time.sleep(0.05)
            progress.update(task, advance=1, description=f"[cyan]Step {i+1}")
        console.print("[bold blue]Progress complete![/bold blue]")
        return n

    result = dummy_progress_task(3)
    assert result == 3
    captured = capsys.readouterr()
    # The progress bar is handled by Rich, but our print should be present
    assert "Progress complete!" in captured.out

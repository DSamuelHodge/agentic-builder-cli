import time
import subprocess
import sys
from pathlib import Path

import pytest


def test_cli_startup_time():
    """
    Performance test to measure CLI startup time.
    Runs `restack-gen --help` and measures execution time.
    """
    start_time = time.time()

    # Run the CLI with --help to measure startup
    result = subprocess.run(
        [sys.executable, "-m", "restack_gen", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )

    end_time = time.time()
    startup_time = end_time - start_time

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "restack-gen" in result.stdout, "Help output not found"

    # Assert startup time is reasonable (less than 2 seconds)
    assert startup_time < 2.0, f"Startup time too slow: {startup_time:.2f}s"

    print(f"CLI startup time: {startup_time:.2f}s")


def test_import_time():
    """
    Performance test to measure import time for main modules.
    """
    modules_to_test = [
        "restack_gen",
        "restack_gen.cli",
        "restack_gen.commands.new",
        "restack_gen.interactive.session",
    ]

    for module in modules_to_test:
        start_time = time.time()
        try:
            __import__(module)
        except ImportError as e:
            pytest.fail(f"Failed to import {module}: {e}")
        end_time = time.time()
        import_time = end_time - start_time

        # Assert import time is reasonable (less than 0.5 seconds per module)
        assert import_time < 0.5, f"Import time for {module} too slow: {import_time:.2f}s"

        print(f"Import time for {module}: {import_time:.2f}s")
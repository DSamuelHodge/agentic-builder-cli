from restack_gen.utils.telemetry import get_collector
from restack_gen.commands.info import TelemetryCommand
from io import StringIO
import sys


def capture_output(func, *args, **kwargs):
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        func(*args, **kwargs)
        return sys.stdout.getvalue(), sys.stderr.getvalue()
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def test_telemetry_enable_disable_status(tmp_path):
    collector = get_collector()
    # Make sure collector is off at start
    collector.disable()

    # Show status when disabled
    cmd = TelemetryCommand(None)
    out, err = capture_output(cmd.execute, [])
    assert "Telemetry is currently disabled." in out

    # Enable
    out, err = capture_output(cmd.execute, ["enable"])
    assert "Telemetry enabled" in out
    assert collector.is_enabled() is True

    # Status returns enabled
    out, err = capture_output(cmd.execute, ["status"])
    assert "Telemetry is currently enabled." in out

    # Disable again
    out, err = capture_output(cmd.execute, ["disable"])
    assert "Telemetry disabled." in out
    assert collector.is_enabled() is False

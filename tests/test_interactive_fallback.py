from restack_gen.interactive import fallback
import sys


def test_fallback_non_tty(monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    ok, reason = fallback.can_use_interactive()
    assert not ok
    assert "TTY" in reason


def test_fallback_requires_ptk(monkeypatch):
    # Remove prompt_toolkit if present
    # Simulate prompt_toolkit not installed by patching find_spec to return None

    import restack_gen.interactive.fallback as fb

    monkeypatch.setattr(fb.importlib_util, "find_spec", lambda name: None)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    ok, reason = fallback.can_use_interactive()
    assert not ok
    assert "prompt-toolkit" in reason

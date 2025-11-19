from restack_gen.__main__ import should_use_interactive_mode


def test_explicit_interactive_flag_short():
    assert should_use_interactive_mode(["-i"])


def test_explicit_interactive_flag_long():
    assert should_use_interactive_mode(["--interactive"])


def test_help_uses_cli():
    assert not should_use_interactive_mode(["--help"])


def test_standard_command_uses_cli():
    assert not should_use_interactive_mode(["new", "my-app"])


def test_no_args_tty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    assert should_use_interactive_mode([])


def test_non_tty_no_args(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    assert not should_use_interactive_mode([])

import sys
from restack_gen import cli


def test_create_parser_and_build_config():
    parser = cli.create_parser()
    args = parser.parse_args(
        [
            "generate",
            "--lang",
            "py",
            "--cwd",
            ".",
            "--force",
            "--dry-run",
            "-q",
            "-v",
            "-y",
            "--no-color",
        ]
    )
    config = cli.build_config(args)
    if args.lang:
        assert config.lang == cli.Language.PYTHON
    else:
        assert config.lang is None
    assert isinstance(config.cwd, cli.Path)
    assert config.cwd == cli.Path(".")
    assert config.force
    assert config.dry_run
    assert config.quiet
    assert config.verbose
    assert config.yes
    assert config.no_color


def test_main_help(monkeypatch, capsys):
    # Simulate sys.argv for help
    monkeypatch.setattr(sys, "argv", ["restack-gen", "--help"])
    called = {}

    class DummyHelp:
        def __init__(self, config):
            pass

        def execute(self, args):
            called["help"] = True
            print("Help shown")
            return 0

    monkeypatch.setattr("restack_gen.commands.info.HelpCommand", DummyHelp)
    result = cli.main()
    out = capsys.readouterr().out
    assert result == 0
    assert "Help shown" in out
    assert called["help"]


def test_main_unknown_command(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["restack-gen", "unknown"])

    class DummyRegistry:
        def __init__(self, config):
            pass

        def get(self, command):
            return None

    monkeypatch.setattr("restack_gen.cli.CommandRegistry", DummyRegistry)
    result = cli.main()
    out = capsys.readouterr().out
    assert result == 1
    assert "Unknown command" in out


def test_main_keyboard_interrupt(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["restack-gen", "generate"])

    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            raise KeyboardInterrupt()

    class DummyRegistry:
        def __init__(self, config):
            pass

        def get(self, command):
            return DummyCommand(None)

    monkeypatch.setattr("restack_gen.cli.CommandRegistry", DummyRegistry)
    result = cli.main()
    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert result == 130
    assert "Cancelled by user" in err


def test_main_unexpected_exception(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["restack-gen", "generate"])

    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            raise Exception("fail")

    class DummyRegistry:
        def __init__(self, config):
            pass

        def get(self, command):
            return DummyCommand(None)

    monkeypatch.setattr("restack_gen.cli.CommandRegistry", DummyRegistry)
    result = cli.main()
    out = capsys.readouterr().out
    assert result == 1
    assert "Unexpected error" in out

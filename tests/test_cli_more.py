from unittest.mock import MagicMock

from restack_gen.cli import (
    ConcurrentProjectCreator,
    create_parser,
    build_config,
    execute_command,
    show_help,
    configure_output,
    handle_concurrent_new,
)
from restack_gen.constants import Config
from restack_gen.cli import ExitCode


def test_create_parser_basic():
    parser = create_parser()
    ns = parser.parse_args(["new", "myapp"])
    assert ns.command == "new"


def test_build_config_and_show_help(capsys):
    parser = create_parser()
    ns = parser.parse_args(["-h"])  # help flag
    # build_config should not raise
    _ = build_config(ns)
    # show_help prints usage
    rc = show_help()
    assert rc == ExitCode.SUCCESS


def test_configure_output_disables_colors(monkeypatch):
    # Force no TTY and assert Color.disable called
    args = MagicMock()
    args.no_color = True
    # Patch stdout to appear non-tty
    monkeypatch.setattr("sys.stdout", type("S", (), {"isatty": lambda self: False})())
    # Spy on disable
    from restack_gen.utils import console

    called = []

    def _fake_disable():
        called.append(True)

    monkeypatch.setattr(console.Color, "disable", _fake_disable)
    configure_output(args)
    assert called


def test_execute_command_unknown(monkeypatch):
    # Unknown command should return error
    cfg = Config()
    rc = execute_command("nope", [], cfg)
    assert rc == ExitCode.ERROR


def test_report_results_various(capsys):
    cfg = Config()
    creator = ConcurrentProjectCreator(cfg)
    results = {"a": ExitCode.SUCCESS, "b": ExitCode.ERROR}
    rc = creator._report_results(results)
    assert rc == ExitCode.ERROR
    captured = capsys.readouterr()
    assert "Failed to create" in captured.out

    results = {"a": ExitCode.SUCCESS}
    rc = creator._report_results(results)
    assert rc == ExitCode.SUCCESS


def test_handle_concurrent_new_empty():
    cfg = Config()
    rc = handle_concurrent_new([], cfg)
    assert rc == ExitCode.ERROR


def test_create_projects_cleanup_on_failure(monkeypatch, tmp_path, capsys):
    cfg = Config()
    cfg.cwd = tmp_path
    creator = ConcurrentProjectCreator(cfg)

    # Make sure the command returns error and also creates a dir that will be cleaned
    class FakeCmd:
        def __init__(self, cfg):
            self.cfg = cfg

        def execute(self, args):
            # Create a directory to simulate partial output
            app_dir = self.cfg.cwd / args[0]
            app_dir.mkdir(parents=True, exist_ok=True)
            return ExitCode.ERROR

        def _get_app_directory(self, name):
            return self.cfg.cwd / name

    monkeypatch.setattr("restack_gen.commands.new.NewCommand", FakeCmd)

    rc = creator.create_projects(["p1"])  # decorator will supply progress
    assert rc == ExitCode.ERROR
    # Ensure cleanup removed the directory
    assert not (cfg.cwd / "p1").exists()

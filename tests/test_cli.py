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
    _, err = captured.out, captured.err
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


def test_execute_command_success(monkeypatch):
    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            return 0

    class DummyRegistry:
        def __init__(self, config):
            pass

        def get(self, command):
            return DummyCommand(None)

    monkeypatch.setattr("restack_gen.cli.CommandRegistry", DummyRegistry)
    result = cli.execute_command("test", [], cli.Config())
    assert result == 0


def test_execute_command_unknown(monkeypatch, capsys):
    class DummyRegistry:
        def __init__(self, config):
            pass

        def get(self, command):
            return None

    monkeypatch.setattr("restack_gen.cli.CommandRegistry", DummyRegistry)
    result = cli.execute_command("unknown", [], cli.Config())
    assert result == 1
    out = capsys.readouterr().out
    assert "Unknown command" in out


def test_show_help(monkeypatch):
    called = {}

    class DummyHelp:
        def __init__(self, config):
            pass

        def execute(self, args):
            called["help"] = True
            return 0

    monkeypatch.setattr("restack_gen.commands.info.HelpCommand", DummyHelp)
    result = cli.show_help()
    assert result == 0
    assert called["help"]


def test_configure_output_no_color():
    class MockArgs:
        no_color = True

    cli.configure_output(MockArgs())
    # This should disable color, but we can't easily test the Color class


def test_main_concurrent_new_success(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["restack-gen", "--concurrent-new", "proj1", "proj2"]
    )

    class DummyCreator:
        def __init__(self, config):
            pass

        def create_projects(self, names):
            return 0

    monkeypatch.setattr("restack_gen.cli.ConcurrentProjectCreator", DummyCreator)
    result = cli.main()
    assert result == 0


def test_main_concurrent_new_empty(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["restack-gen", "--concurrent-new"])

    class DummyCreator:
        def __init__(self, config):
            pass

        def create_projects(self, names):
            return 1  # Error for empty list

    monkeypatch.setattr("restack_gen.cli.ConcurrentProjectCreator", DummyCreator)
    result = cli.main()
    assert result == 1


def test_concurrent_project_creator_empty_projects():
    creator = cli.ConcurrentProjectCreator(cli.Config())
    result = creator.create_projects([])
    assert result == 1


def test_concurrent_project_creator_success(monkeypatch, capsys):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    # Mock successful project creation
    def mock_create_single(name):
        return (name, 0)

    monkeypatch.setattr(creator, "_create_single_project", mock_create_single)
    result = creator.create_projects(["proj1", "proj2"])
    assert result == 0
    out = capsys.readouterr().out
    assert "✓ proj1" in out
    assert "✓ proj2" in out


def test_concurrent_project_creator_failure(monkeypatch, capsys):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    # Mock failed project creation
    def mock_create_single(name):
        return (name, 1)

    monkeypatch.setattr(creator, "_create_single_project", mock_create_single)
    result = creator.create_projects(["proj1"])
    assert result == 1
    out = capsys.readouterr().out
    assert "✗ proj1" in out


def test_concurrent_project_creator_mixed_results(monkeypatch, capsys):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    # Mock mixed results
    def mock_create_single(name):
        if name == "proj1":
            return (name, 0)
        else:
            return (name, 1)

    monkeypatch.setattr(creator, "_create_single_project", mock_create_single)
    result = creator.create_projects(["proj1", "proj2"])
    assert result == 1
    out = capsys.readouterr().out
    assert "✓ proj1" in out
    assert "✗ proj2" in out


def test_concurrent_project_creator_verbose_error(monkeypatch, capsys):
    config = cli.Config()
    config.verbose = True
    creator = cli.ConcurrentProjectCreator(config)

    # Mock exception in project creation
    def mock_create_single(name):
        raise Exception("test error")

    monkeypatch.setattr(creator, "_create_single_project", mock_create_single)
    result = creator.create_projects(["proj1"])
    assert result == 1
    out = capsys.readouterr().out
    assert "✗ proj1" in out


def test_concurrent_project_creator_quiet_mode(monkeypatch, capsys):
    config = cli.Config()
    config.quiet = True
    creator = cli.ConcurrentProjectCreator(config)

    def mock_create_single(name):
        return (name, 0)

    monkeypatch.setattr(creator, "_create_single_project", mock_create_single)
    result = creator.create_projects(["proj1"])
    assert result == 0
    # In quiet mode, should not print progress
    out = capsys.readouterr().out
    assert "✓ proj1" not in out


def test_create_single_project_success(monkeypatch):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            return 0

    monkeypatch.setattr("restack_gen.commands.new.NewCommand", DummyCommand)
    result = creator._create_single_project("testproj")
    assert result == ("testproj", 0)


def test_create_single_project_failure(monkeypatch):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            return 1

    monkeypatch.setattr("restack_gen.commands.new.NewCommand", DummyCommand)
    result = creator._create_single_project("testproj")
    assert result == ("testproj", 1)


def test_create_single_project_exception(monkeypatch):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            raise Exception("test error")

    monkeypatch.setattr("restack_gen.commands.new.NewCommand", DummyCommand)
    result = creator._create_single_project("testproj")
    assert result == ("testproj", 1)


def test_cleanup_failed_project(monkeypatch, tmp_path):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    class DummyCommand:
        def __init__(self, config):
            pass

        def _get_app_directory(self, name):
            return tmp_path / name

    # Create a directory to be cleaned up
    test_dir = tmp_path / "testproj"
    test_dir.mkdir()
    (test_dir / "file.txt").write_text("test")

    cmd = DummyCommand(config)
    monkeypatch.setattr(cmd, "_get_app_directory", lambda name: test_dir)

    creator._cleanup_failed_project(cmd, "testproj")
    assert not test_dir.exists()


def test_report_results_all_success(monkeypatch, capsys):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    results = {"proj1": 0, "proj2": 0}
    result = creator._report_results(results)
    assert result == 0
    out = capsys.readouterr().out
    assert "All projects created successfully" in out


def test_report_results_some_failures(monkeypatch, capsys):
    config = cli.Config()
    creator = cli.ConcurrentProjectCreator(config)

    results = {"proj1": 0, "proj2": 1}
    result = creator._report_results(results)
    assert result == 1
    out = capsys.readouterr().out
    assert "Failed to create: proj2" in out
    assert "Successfully created: proj1" in out


def test_report_results_quiet_mode(monkeypatch, capsys):
    config = cli.Config()
    config.quiet = True
    creator = cli.ConcurrentProjectCreator(config)

    results = {"proj1": 0}
    result = creator._report_results(results)
    assert result == 0
    # Should not print success message in quiet mode
    out = capsys.readouterr().out
    assert "All projects created successfully" not in out


def test_main_unexpected_exception_verbose(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["restack-gen", "generate", "-v"])

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
    assert result == 1
    captured = capsys.readouterr()
    # Should show traceback in verbose mode
    assert "Traceback" in captured.out or "Traceback" in captured.err


def test_main_no_command():
    # Test with no command (should show help)
    result = cli.main([])
    assert result == 0


def test_create_single_project_exception_verbose(monkeypatch, capsys):
    config = cli.Config()
    config.verbose = True
    creator = cli.ConcurrentProjectCreator(config)

    class DummyCommand:
        def __init__(self, config):
            pass

        def execute(self, args):
            raise Exception("test error")

    monkeypatch.setattr("restack_gen.commands.new.NewCommand", DummyCommand)
    result = creator._create_single_project("testproj")
    assert result == ("testproj", 1)
    captured = capsys.readouterr()
    assert "Exception while creating testproj" in captured.out


def test_cleanup_failed_project_verbose(monkeypatch, capsys, tmp_path):
    config = cli.Config()
    config.verbose = True
    creator = cli.ConcurrentProjectCreator(config)

    class DummyCommand:
        def __init__(self, config):
            pass

        def _get_app_directory(self, name):
            return tmp_path / name

    # Create a directory
    test_dir = tmp_path / "testproj"
    test_dir.mkdir()

    cmd = DummyCommand(config)
    # Mock shutil.rmtree to raise an exception
    import shutil

    # Keep a reference to original rmtree if needed
    _ = shutil.rmtree

    def mock_rmtree(path, ignore_errors=False):
        raise Exception("Mock cleanup error")

    monkeypatch.setattr(shutil, "rmtree", mock_rmtree)

    creator._cleanup_failed_project(cmd, "testproj")
    captured = capsys.readouterr()
    assert "Failed to cleanup testproj" in captured.out


def test_main_script_execution():
    # The if __name__ == "__main__" block is hard to test directly
    # but we can verify the main function exists and can be called
    result = cli.main(["--help"])
    assert isinstance(result, int)

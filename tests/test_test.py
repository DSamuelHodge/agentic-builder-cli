from restack_gen.commands.test import RestackTestsCommand
from restack_gen.constants import Config
import subprocess


def test_restack_tests_command_dry_run(tmp_path):
    config = Config()
    config.cwd = tmp_path
    config.dry_run = True
    cmd = RestackTestsCommand(config)

    result = cmd.execute([])
    assert result == 0


def test_restack_tests_command_success(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to return success
    mock_result = type("MockResult", (), {"returncode": 0})()
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    result = cmd.execute([])
    assert result == 0


def test_restack_tests_command_failure(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to return failure
    mock_result = type("MockResult", (), {"returncode": 1})()
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    result = cmd.execute([])
    assert result == 1


def test_restack_tests_command_with_args(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to capture arguments
    called_args = []

    def mock_run(args, **kwargs):
        called_args.extend(args)
        result = type("MockResult", (), {"returncode": 0})()
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = cmd.execute(["--verbose", "specific_test.py"])
    assert result == 0
    assert "pytest" in called_args
    assert "tests" in called_args
    assert "--verbose" in called_args
    assert "specific_test.py" in called_args


def test_restack_tests_command_pytest_not_found(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to raise FileNotFoundError
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            FileNotFoundError("pytest not found")
        ),
    )

    result = cmd.execute([])
    assert result == 1


def test_restack_tests_command_working_directory(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to capture cwd
    called_kwargs = {}

    def mock_run(args, cwd=None, **kwargs):
        called_kwargs["cwd"] = cwd
        result = type("MockResult", (), {"returncode": 0})()
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = cmd.execute([])
    assert result == 0
    assert called_kwargs["cwd"] == tmp_path


def test_restack_tests_command_exception_handling(tmp_path, monkeypatch, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to raise a general exception
    def mock_run(*args, **kwargs):
        raise Exception("unexpected error")

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = cmd.execute([])

    assert result == 1
    captured = capsys.readouterr()
    assert "Running tests..." in captured.out
    assert "unexpected error" in captured.out


def test_restack_tests_command_empty_args(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = RestackTestsCommand(config)

    # Mock subprocess.run to capture arguments
    called_args = []

    def mock_run(args, **kwargs):
        called_args.extend(args)
        result = type("MockResult", (), {"returncode": 0})()
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = cmd.execute([])
    assert result == 0
    assert called_args == ["pytest", "tests"]

from restack_gen.commands.build import BuildCommand
from restack_gen.constants import Config


def test_build_command_dry_run(capsys):
    config = Config()
    config.dry_run = True
    cmd = BuildCommand(config)
    result = cmd.execute([])
    out = capsys.readouterr().out
    assert result == 0
    assert "Would run" in out


def test_build_command_all_pass(monkeypatch, capsys, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = BuildCommand(config)
    # Patch subprocess.run to always succeed
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": ""})(),
    )
    result = cmd.execute([])
    out = capsys.readouterr().out
    assert result == 0
    assert "passed" in out


def test_build_command_some_fail(monkeypatch, capsys, tmp_path):
    config = Config()
    config.cwd = tmp_path
    config.verbose = True
    cmd = BuildCommand(config)

    # Patch subprocess.run to fail for the second check
    def fake_run(cmd_args, **kwargs):
        if "ruff" in cmd_args:
            return type("R", (), {"returncode": 1, "stdout": "ruff error"})()
        return type("R", (), {"returncode": 0, "stdout": ""})()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = cmd.execute([])
    out = capsys.readouterr().out
    assert result == 1
    assert "failed" in out
    assert "ruff error" in out


def test_build_command_tool_not_found(monkeypatch, capsys, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = BuildCommand(config)

    # Patch subprocess.run to raise FileNotFoundError for mypy
    def fake_run(cmd_args, **kwargs):
        if "mypy" in cmd_args:
            raise FileNotFoundError()
        return type("R", (), {"returncode": 0, "stdout": ""})()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = cmd.execute([])
    out = capsys.readouterr().out
    assert result == 0
    assert "tool not found" in out

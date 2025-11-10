import pytest
from restack_gen.commands.dev import DevCommand
from restack_gen.constants import Config


def test_dev_command_script_not_found(tmp_path, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)
    result = cmd.execute([])
    out = capsys.readouterr().out
    assert result == 1
    assert "not found" in out


def test_dev_command_dry_run(tmp_path, capsys):
    config = Config()
    config.cwd = tmp_path
    config.dry_run = True
    cmd = DevCommand(config)
    # Create the script so it would be found
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_engine.sh").write_text("echo hi")
    # Patch ProjectStructure to use our scripts_dir
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(cmd, "dry_run_log", lambda msg: None)
    result = cmd.execute([])
    assert result == 0
    monkeypatch.undo()

import pytest
from restack_gen.commands.dev import DevCommand
from restack_gen.constants import Config
import sys
import subprocess


def test_dev_command_script_not_found(tmp_path, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)
    result = cmd.execute([])
    out = capsys.readouterr().out
    assert result == 1
    assert "No run_engine script found" in out


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


def test_dev_command_windows_bat_script(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory and .bat file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    bat_script = scripts_dir / "run_engine.bat"
    bat_script.write_text("echo test")

    # Mock sys.platform to be Windows
    monkeypatch.setattr(sys, "platform", "win32")

    # Mock subprocess.run to return success
    mock_result = type("MockResult", (), {"returncode": 0})()
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    result = cmd.execute([])
    assert result == 0


def test_dev_command_windows_sh_script_with_bash(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory and .sh file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo test")

    # Mock sys.platform to be Windows
    monkeypatch.setattr(sys, "platform", "win32")

    # Mock shutil.which to return bash path
    import shutil

    monkeypatch.setattr(
        shutil, "which", lambda cmd: "/usr/bin/bash" if cmd == "bash" else None
    )

    # Mock subprocess.run to return success
    mock_result = type("MockResult", (), {"returncode": 0})()
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    result = cmd.execute([])
    assert result == 0


def test_dev_command_windows_sh_script_no_bash(tmp_path, monkeypatch, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory and .sh file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo test")

    # Mock sys.platform to be Windows
    monkeypatch.setattr(sys, "platform", "win32")

    # Mock shutil.which to return None (no bash)
    import shutil

    monkeypatch.setattr(shutil, "which", lambda cmd: None)

    result = cmd.execute([])
    assert result == 1
    captured = capsys.readouterr()
    assert "Bash is required to run .sh scripts on Windows" in captured.out


def test_dev_command_unix_script(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory and .sh file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo test")

    # Mock sys.platform to be Linux
    monkeypatch.setattr(sys, "platform", "linux")

    # Mock subprocess.run to return success
    mock_result = type("MockResult", (), {"returncode": 0})()
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    result = cmd.execute([])
    assert result == 0


def test_dev_command_script_execution_failure(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory and .sh file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo test")

    # Mock sys.platform to be Linux
    monkeypatch.setattr(sys, "platform", "linux")

    # Mock subprocess.run to return failure
    mock_result = type("MockResult", (), {"returncode": 1})()
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    result = cmd.execute([])
    assert result == 1


def test_dev_command_exception_handling(tmp_path, monkeypatch, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory and .sh file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo test")

    # Mock sys.platform to be Linux
    monkeypatch.setattr(sys, "platform", "linux")

    # Mock subprocess.run to raise exception
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(Exception("subprocess error")),
    )

    result = cmd.execute([])
    assert result == 1
    captured = capsys.readouterr()
    assert "Failed to start dev server" in captured.out


def test_dev_command_prefers_bat_on_windows(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory with both .bat and .sh files
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    bat_script = scripts_dir / "run_engine.bat"
    bat_script.write_text("echo bat")
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo sh")

    # Mock sys.platform to be Windows
    monkeypatch.setattr(sys, "platform", "win32")

    # Mock subprocess.run to capture what was called
    called_with = []

    def mock_run(cmd_args, **kwargs):
        called_with.extend(cmd_args)
        result = type("MockResult", (), {"returncode": 0})()
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = cmd.execute([])
    assert result == 0
    # Should have called the .bat script
    assert str(bat_script) in called_with


def test_dev_command_falls_back_to_sh_on_windows(tmp_path, monkeypatch):
    config = Config()
    config.cwd = tmp_path
    cmd = DevCommand(config)

    # Create scripts directory with only .sh file
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    sh_script = scripts_dir / "run_engine.sh"
    sh_script.write_text("echo sh")

    # Mock sys.platform to be Windows
    monkeypatch.setattr(sys, "platform", "win32")

    # Mock shutil.which to return bash path
    import shutil

    monkeypatch.setattr(
        shutil, "which", lambda cmd: "/usr/bin/bash" if cmd == "bash" else None
    )

    # Mock subprocess.run to capture what was called
    called_with = []

    def mock_run(cmd_args, **kwargs):
        called_with.extend(cmd_args)
        result = type("MockResult", (), {"returncode": 0})()
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = cmd.execute([])
    assert result == 0
    # Should have called bash with the .sh script
    assert "/usr/bin/bash" in called_with
    assert str(sh_script) in called_with

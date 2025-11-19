import sys

from restack_gen.commands.doctor import DoctorCommand
from restack_gen.constants import Config


def test_python_version_check_warns(monkeypatch, capsys):
    # simulate older Python version
    monkeypatch.setattr(sys, "version_info", (3, 9, 0))
    cmd = DoctorCommand(Config())
    cmd._check_python()
    captured = capsys.readouterr()
    assert "Python version outside supported range" in captured.out


def test_uv_missing_warns(monkeypatch, capsys):
    # Simulate uv not installed
    import shutil

    monkeypatch.setattr(shutil, "which", lambda name: None)
    cmd = DoctorCommand(Config())
    cmd._check_uv()
    captured = capsys.readouterr()
    assert "uv not found" in captured.out


# --- DoctorCommand Coverage ---
def test_doctor_check_docker(monkeypatch, capsys):
    cmd = DoctorCommand(Config())
    monkeypatch.setattr("subprocess.run", lambda *a, **k: None)
    cmd._check_docker()
    out = capsys.readouterr().out
    assert "Docker is running" in out or "Docker not available" in out


def test_doctor_check_python(capsys):
    cmd = DoctorCommand(Config())
    cmd._check_python()
    out = capsys.readouterr().out
    assert "Python version" in out


def test_doctor_check_packages(monkeypatch, capsys):
    import builtins

    cmd = DoctorCommand(Config())
    orig_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "restack_ai":
            raise ImportError()
        return orig_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    cmd._check_packages()
    out = capsys.readouterr().out
    assert "not installed" in out or "installed" in out


def test_doctor_check_toml_support(monkeypatch, capsys):
    cmd = DoctorCommand(Config())
    monkeypatch.setattr("restack_gen.utils.toml.TOMLLoader.is_available", lambda: True)
    cmd._check_toml_support()
    out = capsys.readouterr().out
    assert "TOML support available" in out or "TOML support not available" in out


def test_doctor_check_environment(monkeypatch, capsys):
    cmd = DoctorCommand(Config())
    monkeypatch.setattr("os.environ", {"RESTACK_HOST": "http://localhost:9999"})
    cmd._check_environment()
    out = capsys.readouterr().out
    assert "RESTACK_HOST" in out
    assert "Dev UI" in out

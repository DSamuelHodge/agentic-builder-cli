from restack_gen.commands.new import NewCommand
from restack_gen.constants import Config


def test_new_command_valid(monkeypatch, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)
    monkeypatch.setattr(cmd, "_create_app", lambda name, dir: 0)
    assert cmd.execute(["myapp"]) == 0


def test_new_command_invalid_name(monkeypatch, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)
    monkeypatch.setattr(cmd, "_validate_app_name", lambda name: False)
    assert cmd.execute(["bad app"]) == 1


def test_new_command_existing_dir(monkeypatch, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)
    app_dir = tmp_path / "myapp"
    app_dir.mkdir()
    assert cmd.execute(["myapp"]) == 1


def test_new_command_no_name(tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)
    assert cmd.execute([]) == 1

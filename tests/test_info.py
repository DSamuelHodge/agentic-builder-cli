from restack_gen.commands.info import VersionCommand, ListTemplatesCommand
from restack_gen.constants import Config


def test_version_command(capsys):
    cmd = VersionCommand(Config())
    cmd.execute([])
    out = capsys.readouterr().out
    assert "restack-gen version" in out


def test_list_templates_command(tmp_path, capsys):
    # Create fake template structure
    templates_root = tmp_path / "templates"
    py_dir = templates_root / "py"
    py_dir.mkdir(parents=True)
    (py_dir / "foo").write_text("")
    config = Config()
    cmd = ListTemplatesCommand(config, templates_root=templates_root)
    cmd.execute([])
    out = capsys.readouterr().out
    assert "Available Templates" in out or "Templates (py):" in out

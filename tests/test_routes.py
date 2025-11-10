from restack_gen.commands.routes import RoutesCommand
from restack_gen.constants import Config


def test_routes_command_empty(monkeypatch, tmp_path, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = RoutesCommand(config)
    # Patch ProjectStructure to use tmp_path
    monkeypatch.setattr(cmd, "_find_files", lambda project, pattern: [])
    cmd.execute([])
    out = capsys.readouterr().out
    assert "No routes found" in out

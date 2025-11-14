from restack_gen.commands.routes import RoutesCommand
from restack_gen.constants import Config


def test_routes_command_empty(tmp_path, capsys):
    config = Config()
    config.cwd = tmp_path
    cmd = RoutesCommand(config)
    cmd.execute([])
    out = capsys.readouterr().out
    assert "No routes found" in out

from restack_gen.commands.generate import GenerateCommand
from restack_gen.commands.new import NewCommand
from restack_gen.commands.routes import RoutesCommand
from restack_gen.commands.doctor import DoctorCommand
from restack_gen.commands.info import VersionCommand, ListTemplatesCommand, HelpCommand
from restack_gen.constants import Config, Language, GenerationType


# --- GenerateCommand ---
def test_generate_command_type_validation():
    cmd = GenerateCommand(Config())
    assert cmd._validate_type("agent") == GenerationType.AGENT
    assert cmd._validate_type("function") == GenerationType.FUNCTION
    assert cmd._validate_type("workflow") == GenerationType.WORKFLOW
    assert cmd._validate_type("badtype") is None


def test_generate_command_name_validation():
    cmd = GenerateCommand(Config())
    assert cmd._validate_name("valid_name")
    assert not cmd._validate_name("123bad")


# --- NewCommand ---
def test_new_command_validate_app_name():
    cmd = NewCommand(Config())
    assert cmd._validate_app_name("myapp")
    assert not cmd._validate_app_name("123bad")


def test_new_command_get_app_directory(tmp_path):
    cmd = NewCommand(Config(cwd=tmp_path))
    app_dir = cmd._get_app_directory("foo")
    assert app_dir == tmp_path / "foo"


# --- RoutesCommand ---
def test_routes_command_print_section(capsys, tmp_path):
    cmd = RoutesCommand(Config(cwd=tmp_path))
    # Create service.py with registered components
    service_py = tmp_path / "service.py"
    service_py.write_text(
        """
from restack_ai import Restack

client = Restack()

async def main():
    await client.start_service(
        agents=[AgentTest],
        workflows=[WorkflowTest],
        functions=[function_test]
    )
"""
    )
    # Should print all sections
    cmd.execute([])
    out = capsys.readouterr().out
    assert "Agents" in out
    assert "Workflows" in out
    assert "Functions" in out


# --- VersionCommand ---
def test_version_command_prints_version(capsys):
    cmd = VersionCommand(Config())
    cmd.execute([])
    out = capsys.readouterr().out
    assert "restack-gen version" in out


# --- ListTemplatesCommand ---
def test_list_templates_command(tmp_path, capsys):
    templates_root = tmp_path / "templates"
    py_dir = templates_root / "py"
    py_dir.mkdir(parents=True)
    (py_dir / "foo.j2").write_text("hi", encoding="utf-8")
    config = Config()
    config.lang = Language.PYTHON
    cmd = ListTemplatesCommand(config, templates_root=templates_root)
    cmd.execute([])
    out = capsys.readouterr().out
    assert "foo.j2" in out


# --- HelpCommand ---
def test_help_command_prints_help(capsys):
    cmd = HelpCommand(Config())
    cmd.execute([])
    out = capsys.readouterr().out
    assert "USAGE" in out
    assert "COMMANDS" in out


# --- DoctorCommand ---
def test_doctor_command_runs(monkeypatch, capsys):
    import sys
    from collections import namedtuple

    cmd = DoctorCommand(Config())
    monkeypatch.setattr("subprocess.run", lambda *a, **k: None)
    VersionInfo = namedtuple("VersionInfo", "major minor micro")
    monkeypatch.setattr(sys, "version_info", VersionInfo(3, 9, 1))
    monkeypatch.setattr("os.environ", {"RESTACK_HOST": "http://localhost:1234"})
    cmd.execute([])
    out = capsys.readouterr().out
    assert "Environment Diagnostics" in out
    assert "Python version" in out
    assert "RESTACK_HOST" in out

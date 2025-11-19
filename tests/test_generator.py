from restack_gen.commands.generate import GenerateCommand
from restack_gen.constants import Config, GenerationType, Language
import pytest
from pathlib import Path


# --- GenerateCommand Coverage ---
def test_generate_validate_type_and_name():
    cmd = GenerateCommand(Config())
    assert cmd._validate_type("agent") == GenerationType.AGENT
    assert not cmd._validate_type("badtype")
    assert cmd._validate_name("good_name")
    assert not cmd._validate_name("123bad")


def test_generate_check_overwrite(tmp_path, monkeypatch):
    cmd = GenerateCommand(Config())
    file = tmp_path / "foo.py"
    # File does not exist
    assert cmd._check_overwrite(file)
    # File exists, force
    file.write_text("x")
    cmd.config.force = True
    assert cmd._check_overwrite(file)
    # File exists, not force, not yes, simulate user input
    cmd.config.force = False
    cmd.config.yes = False
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    assert cmd._check_overwrite(file)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    assert not cmd._check_overwrite(file)
    # File exists, yes
    cmd.config.yes = True
    assert not cmd._check_overwrite(file)


def test_generate_detect_language(tmp_path):
    cmd = GenerateCommand(Config())
    proj = type("P", (), {"src_dir": tmp_path})()
    # Only .py file
    (tmp_path / "foo.py").write_text("")
    assert cmd._detect_language(proj).value == "py"
    (tmp_path / "foo.py").unlink()
    # Only .ts file
    (tmp_path / "foo.ts").write_text("")
    assert cmd._detect_language(proj).value == "ts"


def test_generate_detect_language_config_override(tmp_path):
    cmd = GenerateCommand(Config())
    cmd.config.lang = Language.TYPESCRIPT
    proj = type("P", (), {"src_dir": tmp_path})()
    # Config override should take precedence
    (tmp_path / "foo.py").write_text("")
    assert cmd._detect_language(proj) == Language.TYPESCRIPT


def test_generate_detect_language_default():
    cmd = GenerateCommand(Config())
    proj = type("P", (), {"src_dir": Path("/empty")})()
    # No files, should default to Python
    assert cmd._detect_language(proj) == Language.PYTHON


def test_generate_setup_engine():
    cmd = GenerateCommand(Config())
    engine = cmd._setup_engine(Language.PYTHON)
    assert engine is not None


def test_generate_setup_engine_missing_templates():
    cmd = GenerateCommand(Config())
    # Mock the template_dir.exists() to return False
    import unittest.mock

    with unittest.mock.patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            cmd._setup_engine(Language.PYTHON)


def test_generate_get_output_path(tmp_path):
    cmd = GenerateCommand(Config())
    from restack_gen.core.project import ProjectStructure

    project = ProjectStructure(tmp_path)
    project.ensure_structure()

    # Test agent
    path = cmd._get_output_path(
        project, GenerationType.AGENT, "MyAgent", Language.PYTHON
    )
    assert path == project.get_subdir("agents") / "my_agent.py"

    # Test function
    path = cmd._get_output_path(
        project, GenerationType.FUNCTION, "myFunction", Language.PYTHON
    )
    assert path == project.get_subdir("functions") / "my_function.py"

    # Test workflow
    path = cmd._get_output_path(
        project, GenerationType.WORKFLOW, "MyWorkflow", Language.TYPESCRIPT
    )
    assert path == project.get_subdir("workflows") / "my_workflow.ts"


def test_generate_execute_insufficient_args():
    cmd = GenerateCommand(Config())
    assert cmd.execute([]) == 1
    assert cmd.execute(["agent"]) == 1


def test_generate_execute_invalid_type():
    cmd = GenerateCommand(Config())
    assert cmd.execute(["invalidtype", "name"]) == 1


def test_generate_execute_invalid_name():
    cmd = GenerateCommand(Config())
    assert cmd.execute(["agent", "123invalid"]) == 1


def test_generate_dry_run(tmp_path):
    cmd = GenerateCommand(Config())
    cmd.config.dry_run = True
    cmd.config.cwd = str(tmp_path)

    # Create minimal project structure
    project_dir = tmp_path / "testproject"
    project_dir.mkdir()
    src_dir = project_dir / "src"
    src_dir.mkdir()
    agents_dir = src_dir / "agents"
    agents_dir.mkdir(parents=True)
    (src_dir / "dummy.py").write_text("")

    result = cmd.execute(["agent", "TestAgent"])
    assert result == 0
    # File should not be created in dry run
    agent_file = agents_dir / "test_agent.py"
    assert not agent_file.exists()


def test_generate_full_flow(tmp_path):
    cmd = GenerateCommand(Config())
    # Set cwd to the project directory
    project_dir = tmp_path / "testproject"
    project_dir.mkdir()
    cmd.config.cwd = str(project_dir)

    # Create minimal project structure
    src_dir = project_dir / "src"
    src_dir.mkdir()
    agents_dir = src_dir / "agents"
    agents_dir.mkdir(parents=True)

    # Create a Python file to detect language
    (src_dir / "dummy.py").write_text("")

    result = cmd.execute(["agent", "TestAgent"])
    assert result == 0
    # Check if file was created
    agent_file = agents_dir / "test_agent.py"
    assert agent_file.exists()
    content = agent_file.read_text()
    assert "TestAgent" in content


def test_generate_with_force_overwrite(tmp_path):
    cmd = GenerateCommand(Config())
    cmd.config.force = True

    # Set cwd to the project directory
    project_dir = tmp_path / "testproject"
    project_dir.mkdir()
    cmd.config.cwd = str(project_dir)

    # Create project structure
    src_dir = project_dir / "src"
    src_dir.mkdir()
    agents_dir = src_dir / "agents"
    agents_dir.mkdir(parents=True)
    (src_dir / "dummy.py").write_text("")

    # Pre-create the file
    agent_file = agents_dir / "test_agent.py"
    agent_file.write_text("old content")

    result = cmd.execute(["agent", "TestAgent"])
    assert result == 0
    content = agent_file.read_text()
    assert "TestAgent" in content
    assert "old content" not in content  # Should be overwritten


def test_generate_exception_handling(tmp_path):
    cmd = GenerateCommand(Config())
    cmd.config.cwd = str(tmp_path)

    # Mock _generate to return 1 (simulating exception handling)
    import unittest.mock

    with unittest.mock.patch.object(cmd, "_generate", return_value=1):
        result = cmd.execute(["agent", "TestAgent"])
        assert result == 1


def test_generate_exception_handling_verbose(tmp_path, capsys):
    cmd = GenerateCommand(Config())
    cmd.config.cwd = str(tmp_path)
    cmd.config.verbose = True

    # Mock _generate to return 1 (simulating exception handling)
    import unittest.mock

    with unittest.mock.patch.object(cmd, "_generate", return_value=1):
        result = cmd.execute(["agent", "TestAgent"])
        assert result == 1
        # For verbose test, we can't easily test the traceback output since it's mocked


def test_generate_typescript_flow(tmp_path):
    cmd = GenerateCommand(Config())
    cmd.config.lang = Language.TYPESCRIPT

    # Set cwd to the project directory
    project_dir = tmp_path / "testproject"
    project_dir.mkdir()
    cmd.config.cwd = str(project_dir)

    # Create project structure
    src_dir = project_dir / "src"
    src_dir.mkdir()
    functions_dir = src_dir / "functions"
    functions_dir.mkdir(parents=True)

    result = cmd.execute(["function", "TestFunction"])
    assert result == 0
    # Check if TypeScript file was created
    func_file = functions_dir / "test_function.ts"
    assert func_file.exists()
    content = func_file.read_text()
    assert "TestFunction" in content

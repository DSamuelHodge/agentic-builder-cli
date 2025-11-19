import pytest

from restack_gen.commands.new import NewCommand
from restack_gen.constants import Config, Language


@pytest.mark.parametrize("lang", [Language.PYTHON, Language.TYPESCRIPT])
def test_project_structure_creation(lang, tmp_path):
    """
    Integration test to verify that NewCommand creates the correct project structure
    for both Python and TypeScript projects.
    """
    project_name = f"test-{lang.value}-project"
    config = Config(lang=lang, cwd=tmp_path, yes=True, quiet=True)

    cmd = NewCommand(config)
    result = cmd.execute([project_name])

    assert result == 0, f"NewCommand failed for {lang.value}"

    project_dir = tmp_path / project_name
    assert project_dir.exists() and project_dir.is_dir()

    # Common structure checks
    assert (project_dir / "README.md").exists()
    # Note: restack.toml is optional and only created if template exists

    if lang == Language.PYTHON:
        # Python-specific checks
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "service.py").exists()
        assert (project_dir / "src").exists() and (project_dir / "src").is_dir()
        assert (project_dir / "src/agents").exists()
        assert (project_dir / "src/functions").exists()
        assert (project_dir / "src/workflows").exists()
        assert (project_dir / "scripts").exists()
        assert (project_dir / "scripts/run_engine.sh").exists()
        assert (project_dir / "tests").exists()
        # Check for sample files
        assert any((project_dir / "src/agents").iterdir())  # At least one agent file
        assert any(
            (project_dir / "src/functions").iterdir()
        )  # At least one function file
        assert any(
            (project_dir / "src/workflows").iterdir()
        )  # At least one workflow file

    elif lang == Language.TYPESCRIPT:
        # TypeScript-specific checks
        assert (project_dir / "tsconfig.json").exists()
        assert (project_dir / "src").exists() and (project_dir / "src").is_dir()
        assert (project_dir / "src/agents").exists()
        assert (project_dir / "src/functions").exists()
        assert (project_dir / "src/workflows").exists()
        # Check for sample files
        assert any((project_dir / "src/agents").iterdir())  # At least one agent file
        assert any(
            (project_dir / "src/functions").iterdir()
        )  # At least one function file
        assert any(
            (project_dir / "src/workflows").iterdir()
        )  # At least one workflow file

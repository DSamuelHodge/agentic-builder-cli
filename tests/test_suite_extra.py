import pytest
from restack_gen.constants import Config
from restack_gen.commands import CommandRegistry
from restack_gen.core.validation import Validator
from restack_gen.core.project import ProjectStructure
from restack_gen.core.templates import TemplateEngine
from restack_gen.utils.toml import TOMLLoader
import os


# --- CommandRegistry Tests ---
def test_command_registry_get():
    config = Config()
    registry = CommandRegistry(config)
    assert registry.get("new") is not None
    assert registry.get("g") is not None
    assert registry.get("help") is not None
    assert registry.get("nonexistent") is None


def test_command_registry_list_commands():
    config = Config()
    registry = CommandRegistry(config)
    commands = registry.list_commands()
    assert "new" in commands
    assert "help" in commands


# --- Integration: Project + TemplateEngine ---
def test_integration_project_template(tmp_path):
    proj = ProjectStructure(tmp_path)
    proj.ensure_structure()
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "foo.j2").write_text("Hi {{ name }}!")
    engine = TemplateEngine(templates_dir)
    result = engine.render("foo.j2", {"name": "Bar"})
    assert result == "Hi Bar!"


# --- TOMLLoader Error Handling ---
def test_toml_loader_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        TOMLLoader.load(tmp_path / "notfound.toml")


def test_toml_loader_parse_error(tmp_path):
    file = tmp_path / "bad.toml"
    file.write_text("not a toml: [")
    if TOMLLoader.is_available():
        with pytest.raises(ValueError):
            TOMLLoader.load(file)


# --- Security: Path Traversal ---
def test_validator_path_traversal():
    from pathlib import Path

    valid, msg = Validator.validate_path(Path(os.path.join("..", "etc", "passwd")))
    assert not valid
    assert "suspicious" in msg.lower()


# --- Security: Name Validation (Injection) ---
def test_validator_name_injection():
    valid, msg = Validator.validate_name("foo;rm -rf /")
    assert not valid


# --- Performance: Large Project Structure ---
def test_large_project_structure(tmp_path):
    proj = ProjectStructure(tmp_path)
    for i in range(100):
        (proj.src_dir / f"agents/agent_{i}.py").parent.mkdir(
            parents=True, exist_ok=True
        )
        (proj.src_dir / f"agents/agent_{i}.py").write_text("")
    files = list(proj.src_dir.glob("agents/*.py"))
    assert len(files) == 100


# --- Compatibility: Unicode Handling ---
def test_unicode_template(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "uni.j2").write_text("Привет {{ name }}!", encoding="utf-8")
    engine = TemplateEngine(templates_dir)
    result = engine.render("uni.j2", {"name": "мир"})
    assert "мир" in result


# --- Regression: Known bug fix ---
def test_validator_keyword_regression():
    valid, msg = Validator.validate_name("class")
    assert not valid
    assert "keyword" in msg.lower()


# --- Edge Case: Empty Name ---
def test_validator_empty_name():
    valid, msg = Validator.validate_name("")
    assert not valid
    assert "empty" in msg.lower()

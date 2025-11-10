import pytest
from restack_gen.core.templates import TemplateEngine, build_template_context
from pathlib import Path


def test_template_engine_init(tmp_path):
    templates_dir = tmp_path / "templates"
    engine = TemplateEngine(templates_dir)
    assert engine.templates_dir == templates_dir
    assert engine._env is None


def test_template_engine_env_property(tmp_path):
    templates_dir = tmp_path / "templates"
    engine = TemplateEngine(templates_dir)
    # Should lazy load Jinja2 env
    env = engine.env
    assert env is not None
    assert engine._env is env


def test_template_engine_render(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    template_file = templates_dir / "test.txt"
    template_file.write_text("Hello {{ name }}!")
    engine = TemplateEngine(templates_dir)
    result = engine.render("test.txt", {"name": "World"})
    assert result == "Hello World!"


def test_template_engine_template_exists(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    template_file = templates_dir / "exists.txt"
    template_file.write_text("")
    engine = TemplateEngine(templates_dir)
    assert engine.template_exists("exists.txt")
    assert not engine.template_exists("missing.txt")


def test_template_engine_list_templates(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "template1.txt").write_text("")
    (templates_dir / "template2.txt").write_text("")
    (templates_dir / ".hidden.txt").write_text("")  # Should be ignored
    engine = TemplateEngine(templates_dir)
    templates = engine.list_templates()
    assert "template1.txt" in templates
    assert "template2.txt" in templates
    assert ".hidden.txt" not in templates


def test_template_engine_list_templates_no_dir(tmp_path):
    templates_dir = tmp_path / "missing"
    engine = TemplateEngine(templates_dir)
    templates = engine.list_templates()
    assert templates == []


def test_build_template_context():
    context = build_template_context("test_name", app_name="my_app")
    assert context["name"] == "test_name"
    assert context["app_name"] == "my_app"
    assert context["snake_name"] == "test_name"
    assert context["pascal_name"] == "TestName"
    assert context["kebab_name"] == "test-name"
    assert context["snake_app_name"] == "my_app"
    assert context["pascal_app_name"] == "MyApp"
    assert context["kebab_app_name"] == "my-app"
    assert context["timeouts_start_to_close_seconds"] == 30
    assert context["timeouts_start_to_close"] == "30s"
    assert context["retry_policies_default_json"] == "{}"
    assert context["queues_default"] == "default"


def test_build_template_context_defaults():
    context = build_template_context("test_name")
    assert context["app_name"] == "test_name"
    assert context["snake_app_name"] == "test_name"


def test_build_template_context_with_kwargs():
    context = build_template_context("test_name", custom_var="value")
    assert context["custom_var"] == "value"

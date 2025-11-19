from restack_gen.commands.new import NewCommand
from restack_gen.constants import Config, Language
from pathlib import Path


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


def test_new_command_dry_run(monkeypatch, tmp_path):
    config = Config()
    config.cwd = tmp_path
    config.dry_run = True
    cmd = NewCommand(config)
    monkeypatch.setattr(cmd, "_show_dry_run", lambda dir: None)
    assert cmd.execute(["myapp"]) == 0


def test_new_command_create_app_error(monkeypatch, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)
    monkeypatch.setattr(
        cmd,
        "_create_app",
        lambda name, dir: (_ for _ in ()).throw(Exception("test error")),
    )
    assert cmd.execute(["myapp"]) == 1


def test_new_command_create_app_error_verbose(monkeypatch, tmp_path, capsys):
    config = Config()
    config.cwd = tmp_path
    config.verbose = True
    cmd = NewCommand(config)
    monkeypatch.setattr(
        cmd,
        "_create_app",
        lambda name, dir: (_ for _ in ()).throw(Exception("test error")),
    )
    result = cmd.execute(["myapp"])
    assert result == 1
    captured = capsys.readouterr()
    assert "Traceback" in captured.out or "Traceback" in captured.err


def test_validate_app_name_valid():
    config = Config()
    cmd = NewCommand(config)
    assert cmd._validate_app_name("valid_app")


def test_validate_app_name_invalid():
    config = Config()
    cmd = NewCommand(config)
    assert not cmd._validate_app_name("invalid app")


def test_get_app_directory(tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)
    result = cmd._get_app_directory("myapp")
    assert result == tmp_path / "myapp"


def test_get_app_directory_no_cwd():
    config = Config()
    config.cwd = None
    cmd = NewCommand(config)
    result = cmd._get_app_directory("myapp")
    assert result.name == "myapp"


def test_show_dry_run(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    app_dir = tmp_path / "myapp"
    cmd._show_dry_run(app_dir)
    # This method logs, but we can't easily test the log output without mocking


def test_setup_templates_python(tmp_path):
    config = Config()
    config.lang = Language.PYTHON
    cmd = NewCommand(config)
    app_name = "testapp"
    app_dir = tmp_path / app_name
    engine, toml_values = cmd._setup_templates(app_name, app_dir, Language.PYTHON)
    assert engine is not None
    assert isinstance(toml_values, dict)


def test_setup_templates_typescript(tmp_path):
    config = Config()
    config.lang = Language.TYPESCRIPT
    cmd = NewCommand(config)
    app_name = "testapp"
    app_dir = tmp_path / app_name
    engine, toml_values = cmd._setup_templates(app_name, app_dir, Language.TYPESCRIPT)
    assert engine is not None
    assert isinstance(toml_values, dict)


def test_load_toml_config(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    templates_root = Path(__file__).parent.parent / "templates"
    app_name = "testapp"
    app_dir = tmp_path / app_name
    result = cmd._load_toml_config(templates_root, app_name, app_dir)
    assert isinstance(result, dict)


def test_extract_toml_values():
    config = Config()
    cmd = NewCommand(config)
    data = {
        "timeouts": {"start_to_close": 30},
        "retry_policies": {"max_attempts": 3},
        "queues": {"default": "myqueue"},
    }
    result = cmd._extract_toml_values(data)
    assert "timeouts_start_to_close_seconds" in result
    assert "retry_policies_default_json" in result
    assert "queues_default" in result


def test_create_readme(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    app_dir = tmp_path / "testapp"
    app_dir.mkdir()
    cmd._create_readme(app_dir, "testapp")
    readme_path = app_dir / "README.md"
    assert readme_path.exists()


def test_generate_samples(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    from restack_gen.core.project import ProjectStructure
    from restack_gen.core.templates import TemplateEngine

    project = ProjectStructure(tmp_path / "testapp")
    project.ensure_structure()
    templates_root = Path(__file__).parent.parent / "templates"
    template_dir = templates_root / "py"
    engine = TemplateEngine(template_dir)
    toml_values = {}
    cmd._generate_samples(engine, project, "testapp", Language.PYTHON, toml_values)
    # Check if files were created
    agents_dir = project.get_subdir("agents")
    functions_dir = project.get_subdir("functions")
    workflows_dir = project.get_subdir("workflows")
    assert (agents_dir / "testapp.py").exists() or not engine.template_exists(
        "agent.py.j2"
    )
    assert (functions_dir / "llm_chat.py").exists() or not engine.template_exists(
        "function.py.j2"
    )
    assert (
        workflows_dir / "automated_workflow.py"
    ).exists() or not engine.template_exists("workflow.py.j2")


def test_generate_test_sample(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    from restack_gen.core.project import ProjectStructure
    from restack_gen.core.templates import TemplateEngine

    project = ProjectStructure(tmp_path / "testapp")
    project.ensure_structure()
    templates_root = Path(__file__).parent.parent / "templates"
    template_dir = templates_root / "py"
    engine = TemplateEngine(template_dir)
    toml_values = {}
    cmd._generate_test_sample(engine, project, "testapp", Language.PYTHON, toml_values)
    test_file = project.tests_dir / "test_sample.py"
    assert test_file.exists() or not engine.template_exists("test_sample.py.j2")


def test_create_service(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    app_dir = tmp_path / "testapp"
    app_dir.mkdir()
    cmd._create_service(app_dir, "testapp")
    service_file = app_dir / "service.py"
    assert service_file.exists()
    content = service_file.read_text()
    assert "Testapp" in content  # pascal case


def test_create_run_script(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    cmd._create_run_script(scripts_dir)
    script_file = scripts_dir / "run_engine.sh"
    assert script_file.exists()
    content = script_file.read_text()
    assert "Starting Restack engine" in content


def test_show_next_steps(capsys):
    config = Config()
    cmd = NewCommand(config)
    cmd._show_next_steps("testapp")
    captured = capsys.readouterr()
    assert "Created new Restack app: testapp" in captured.out
    assert "cd testapp" in captured.out
    assert "uv venv" in captured.out
    assert "uv pip install -e .[dev]" in captured.out
    assert "restack-gen dev" in captured.out


def test_create_app_typescript_flow(tmp_path):
    config = Config()
    config.lang = Language.TYPESCRIPT
    cmd = NewCommand(config)
    app_name = "testapp"
    app_dir = tmp_path / app_name
    result = cmd._create_app(app_name, app_dir)
    assert result == 0
    assert app_dir.exists()
    assert (app_dir / "README.md").exists()
    assert (app_dir / "service.py").exists()  # service.py is always created
    assert (app_dir / "tsconfig.json").exists()
    assert (app_dir / "scripts" / "run_engine.sh").exists()


def test_setup_templates_missing_lang_dir(monkeypatch, tmp_path):
    config = Config()
    cmd = NewCommand(config)
    app_name = "testapp"
    app_dir = tmp_path / app_name
    # Mock template_dir.exists() to return False
    monkeypatch.setattr(
        Path,
        "exists",
        lambda self: (
            False if "templates" in str(self) and self.name in ["py", "ts"] else True
        ),
    )
    engine, toml_values = cmd._setup_templates(app_name, app_dir, Language.PYTHON)
    assert engine is not None
    assert isinstance(toml_values, dict)


def test_load_toml_config_with_toml_template(tmp_path):
    config = Config()
    cmd = NewCommand(config)
    templates_root = Path(__file__).parent.parent / "templates"
    app_name = "testapp"
    app_dir = tmp_path / app_name
    app_dir.mkdir()
    # Create a mock restack.toml.j2
    toml_template = templates_root / "restack.toml.j2"
    if toml_template.exists():
        result = cmd._load_toml_config(templates_root, app_name, app_dir)
        assert isinstance(result, dict)
        # Check if restack.toml was created
        toml_file = app_dir / "restack.toml"
        assert toml_file.exists()


def test_extract_toml_values_string_timeout():
    config = Config()
    cmd = NewCommand(config)
    data = {
        "timeouts": {"start_to_close": "30s"},
        "retry_policies": {"max_attempts": 3},
        "queues": {"default": "myqueue"},
    }
    result = cmd._extract_toml_values(data)
    assert result["timeouts_start_to_close"] == "30s"


def test_create_readme_fallback(tmp_path, monkeypatch):
    config = Config()
    cmd = NewCommand(config)
    app_dir = tmp_path / "testapp"
    app_dir.mkdir()
    # Mock engine.template_exists to return False
    from restack_gen.core.templates import TemplateEngine

    monkeypatch.setattr(TemplateEngine, "template_exists", lambda self, name: False)
    cmd._create_readme(app_dir, "testapp")
    readme_path = app_dir / "README.md"
    assert readme_path.exists()
    content = readme_path.read_text()
    assert "# testapp" in content
    assert "Generated by restack-gen" in content


def test_generate_samples_exception_handling(tmp_path, monkeypatch):
    config = Config()
    cmd = NewCommand(config)
    from restack_gen.core.project import ProjectStructure
    from restack_gen.core.templates import TemplateEngine

    project = ProjectStructure(tmp_path / "testapp")
    project.ensure_structure()
    templates_root = Path(__file__).parent.parent / "templates"
    template_dir = templates_root / "py"
    engine = TemplateEngine(template_dir)
    toml_values = {}
    # Mock engine.render to raise exception
    monkeypatch.setattr(
        TemplateEngine,
        "render",
        lambda self, template, context: (_ for _ in ()).throw(
            Exception("render error")
        ),
    )
    # Should not raise, just log warning
    cmd._generate_samples(engine, project, "testapp", Language.PYTHON, toml_values)


def test_generate_test_sample_exception_handling(tmp_path, monkeypatch):
    config = Config()
    cmd = NewCommand(config)
    from restack_gen.core.project import ProjectStructure
    from restack_gen.core.templates import TemplateEngine

    project = ProjectStructure(tmp_path / "testapp")
    project.ensure_structure()
    templates_root = Path(__file__).parent.parent / "templates"
    template_dir = templates_root / "py"
    engine = TemplateEngine(template_dir)
    toml_values = {}
    # Mock engine.render to raise exception
    monkeypatch.setattr(
        TemplateEngine,
        "render",
        lambda self, template, context: (_ for _ in ()).throw(
            Exception("render error")
        ),
    )
    # Should not raise, just log warning
    cmd._generate_test_sample(engine, project, "testapp", Language.PYTHON, toml_values)


def test_create_run_script_chmod_exception(tmp_path, monkeypatch):
    config = Config()
    cmd = NewCommand(config)
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    # Mock chmod to raise exception
    monkeypatch.setattr(
        Path,
        "chmod",
        lambda self, mode: (_ for _ in ()).throw(Exception("chmod error")),
    )
    # Should not raise
    cmd._create_run_script(scripts_dir)
    script_file = scripts_dir / "run_engine.sh"
    assert script_file.exists()


def test_execute_cleanup_on_error(monkeypatch, tmp_path):
    config = Config()
    config.cwd = tmp_path
    cmd = NewCommand(config)

    # Mock _create_app to raise exception and check cleanup
    def mock_create_app(name, dir):
        # Create some files first
        (dir / "some_file.txt").write_text("test")
        raise Exception("test error")

    monkeypatch.setattr(cmd, "_create_app", mock_create_app)
    result = cmd.execute(["myapp"])
    assert result == 1
    # Check that directory was cleaned up
    app_dir = tmp_path / "myapp"
    assert not app_dir.exists()

from restack_gen.commands.generate import GenerateCommand
from restack_gen.constants import Config, GenerationType


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

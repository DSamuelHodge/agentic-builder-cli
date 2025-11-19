import sys
import types


from restack_gen.cli_interactive import InteractiveCLI, ExitCode
from restack_gen.interactive.prompts import InteractivePrompter
from restack_gen.__main__ import should_use_interactive_mode, main as root_main
from restack_gen.constants import Language


def test_prompter_fallback_input_default(monkeypatch):
    monkeypatch.setattr(InteractivePrompter, "_has_prompt_toolkit", lambda self: False)
    # Simulate empty input -> default returned
    monkeypatch.setattr("builtins.input", lambda s="": "")
    prompter = InteractivePrompter(None)
    result = prompter.prompt_input("Language (py/ts)", "py")
    assert result == "py"


def test_prompter_fallback_input_value(monkeypatch):
    monkeypatch.setattr(InteractivePrompter, "_has_prompt_toolkit", lambda self: False)
    monkeypatch.setattr("builtins.input", lambda s="": "ts")
    prompter = InteractivePrompter(None)
    result = prompter.prompt_input("Language (py/ts)", "py")
    assert result == "ts"


def test_prompter_uses_prompt_toolkit(monkeypatch):
    monkeypatch.setattr(InteractivePrompter, "_has_prompt_toolkit", lambda self: True)
    # Replace or inject fake prompt_toolkit to avoid importing the real package
    fake_mod = types.ModuleType("prompt_toolkit")
    fake_mod.prompt = lambda message: "pt-test"
    # Use monkeypatch to ensure restoration
    monkeypatch.setitem(sys.modules, "prompt_toolkit", fake_mod)
    try:
        prompter = InteractivePrompter(None)
        res = prompter.prompt_input("Project name", "demo")
        assert res == "pt-test"
    finally:
        # Restore original module if it was present
        # monkeypatch fixture will restore the original module
        pass


def test_choose_language_default_and_info_print(monkeypatch, capsys):
    cli = InteractiveCLI([])
    # Force no language in config
    cli.config.lang = None
    # Provide invalid language to trigger print_info fallback
    monkeypatch.setattr(cli, "_prompt", lambda message, default=None: "c++")

    lang = cli._choose_language()
    assert lang == Language.PYTHON
    captured = capsys.readouterr()
    assert "Please choose 'py' or 'ts'" in captured.out


def test_handle_new_keyboard_interrupt(monkeypatch):
    # Should return interrupted code when session raises KeyboardInterrupt
    # Make InteractiveSession a factory that accepts the `config` argument
    def _factory(cfg):
        class S:
            def start(self):
                raise KeyboardInterrupt

        return S()

    monkeypatch.setattr("restack_gen.interactive.InteractiveSession", _factory)

    cli = InteractiveCLI([])
    assert cli._handle_new() == ExitCode.INTERRUPTED


def test_handle_new_user_cancel(monkeypatch):
    class FakeResult:
        project_name = "test"
        language = "py"
        package_manager = "uv"
        working_directory = None

    # Return an instance from the fake factory
    monkeypatch.setattr(
        "restack_gen.interactive.InteractiveSession",
        lambda cfg: type("S", (), {"start": lambda self: FakeResult()})(),
    )
    cli = InteractiveCLI([])
    cli.config.cwd = None
    cli.config.yes = False
    # Confirmation will return "n" (no)
    monkeypatch.setattr(cli, "_prompt", lambda msg, default=None: "n")

    result = cli._handle_new()
    # When user says no, it should not error and return success (cancelled)
    assert result == ExitCode.SUCCESS


def test_should_use_interactive_flag_short_and_long():
    assert should_use_interactive_mode(["--interactive"]) is True
    assert should_use_interactive_mode(["-i"]) is True


def test_should_use_interactive_tty(monkeypatch):
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(isatty=lambda: True))
    assert should_use_interactive_mode([]) is True


def test_should_use_interactive_false_for_help():
    assert should_use_interactive_mode(["help"]) is False


def test_root_main_dispatch(monkeypatch):
    # Patch the interactive and standard CLI entrypoints to ensure routing
    monkeypatch.setattr(
        "restack_gen.__main__.should_use_interactive_mode", lambda argv=None: True
    )
    monkeypatch.setattr("restack_gen.cli_interactive.main", lambda argv=None: 5)
    assert root_main([]) == 5


def test_root_main_handles_keyboardinterrupt(monkeypatch, capsys):
    monkeypatch.setattr(
        "restack_gen.__main__.should_use_interactive_mode", lambda argv=None: True
    )

    def raising(*a, **k):
        raise KeyboardInterrupt

    monkeypatch.setattr("restack_gen.cli_interactive.main", raising)
    rc = root_main([])
    assert rc == 130
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.err


def test_root_main_handles_exception(monkeypatch, capsys):
    monkeypatch.setattr(
        "restack_gen.__main__.should_use_interactive_mode", lambda argv=None: True
    )

    def explode(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr("restack_gen.cli_interactive.main", explode)
    rc = root_main([])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Fatal error: boom" in captured.err

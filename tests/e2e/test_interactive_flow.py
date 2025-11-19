import os
import sys
import pytest

import restack_gen.cli_interactive as cli_interactive


@pytest.mark.skipif(
    os.environ.get("CI") == "true", reason="E2E interactive test skipped in CI"
)
def test_interactive_flow(monkeypatch, tmp_path):
    """
    E2E test for the interactive CLI session, mocking prompt_toolkit.prompt and input().
    Simulates a user creating a new project interactively.
    """
    # Simulate user answers for prompts (project name, language, template, etc.)
    user_inputs = iter(
        [
            "new",  # Action: new
            "my-e2e-project",  # Project name
            "py",  # Language
            "uv",  # Package manager
            str(tmp_path),  # Output directory
            "y",  # Confirm
        ]
    )

    def fake_prompt(*args, **kwargs):
        return next(user_inputs)

    def fake_input(prompt=None):
        return next(user_inputs)

    # Patch prompt_toolkit.prompt and built-in input
    monkeypatch.setattr("prompt_toolkit.prompt", fake_prompt, raising=False)
    monkeypatch.setattr("builtins.input", fake_input)

    # Patch sys.argv to simulate `restack-gen -i new`
    monkeypatch.setattr(sys, "argv", ["restack-gen", "-i", "new"])

    # Run the interactive CLI
    result = cli_interactive.InteractiveCLI().run()

    # Check that the project directory was created
    project_dir = tmp_path / "my-e2e-project"
    assert project_dir.exists() and project_dir.is_dir()
    # Check for a key file (e.g., pyproject.toml or agent.py)
    found = any(f.name in ("pyproject.toml", "agent.py") for f in project_dir.iterdir())
    assert found, "Expected project file not found in generated directory"

    # Optionally, check the result object for success
    assert result is None or getattr(result, "success", True)

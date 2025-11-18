"""Interactive prompts and a fallback prompt implementation.

We try to leverage prompt_toolkit if installed; otherwise we fall back
on the built-in input() function. We keep the prompter API simple for
integration with existing commands.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..constants import Config


@dataclass
class PromptResult:
    project_name: str
    language: str
    package_manager: str
    working_directory: Path | None = None
    init_git: bool = True
    include_docker: bool = False
    force: bool = False


class InteractivePrompter:
    def __init__(self, config: 'Config'):
        self.config = config

    def _has_prompt_toolkit(self) -> bool:
        try:
            import prompt_toolkit  # type: ignore

            return True
        except Exception:
            return False

    def prompt_input(self, message: str, default: str | None = None) -> str:
        if self._has_prompt_toolkit():
            from prompt_toolkit import prompt

            full = f"{message} [{default}] " if default else f"{message} "
            value = prompt(full)
            if not value and default is not None:
                return default
            return value
        else:
            if default is not None:
                value = input(f"{message} [{default}] ")
                if not value:
                    return default
                return value
            else:
                return input(f"{message} ")

    def run_full_wizard(self) -> PromptResult:
        project_name = self.prompt_input("Project name")
        language = self.prompt_input("Language (py/ts)", "py").lower()
        package_manager = self.prompt_input("Package manager (uv/pip/pnpm/npm)", "uv").lower()

        if language not in ("py", "ts"):
            language = "py"

        return PromptResult(
            project_name=project_name,
            language=language,
            package_manager=package_manager,
        )
"""Simple interactive session orchestrator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..constants import Config

from .prompts import InteractivePrompter


@dataclass
class PromptResult:
    project_name: str
    language: str
    package_manager: str
    init_git: bool = True
    include_docker: bool = False
    working_directory: str | None = None


class InteractiveSession:
    def __init__(self, config: 'Config'):
        self.config = config
        self.prompter = InteractivePrompter(config)

    def start(self) -> PromptResult:
        result = self.prompter.run_full_wizard()
        return result

    def apply_to_config(self):
        # Convert PromptResult to Config values
        # This simple mapping sets language and package_manager on the global config
        return self.config

    def start_with_template(self, template):
        # Not implemented in this minimal version
        return self.start()
"""Multi-step wizard orchestration for interactive mode."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..constants import Config

from .prompts import InteractivePrompter


@dataclass
class WizardStep:
    id: str
    title: str
    prompt_method: str
    condition: callable | None = None


@dataclass
class WizardResult:
    project_name: str = ""
    language: str = ""
    package_manager: str = ""
    features: list[str] = field(default_factory=list)
    options: dict = field(default_factory=dict)


class ProjectWizard:
    def __init__(self, config: "Config"):
        self.config = config
        self.prompter = InteractivePrompter(config)
        self.result = WizardResult()

    def define_steps(self) -> list[WizardStep]:
        return [
            WizardStep("project_name", "Project", "prompt_project_name"),
            WizardStep("language", "Language", "prompt_language"),
            WizardStep("package_manager", "Package Manager", "prompt_package_manager"),
        ]

    def run(self) -> WizardResult:
        steps = self.define_steps()
        for step in steps:
            if step.condition and not step.condition():
                continue
            method = getattr(self.prompter, step.prompt_method, None)
            if not method:
                continue
            if step.id == "project_name":
                self.result.project_name = method()
            elif step.id == "language":
                self.result.language = method(self.result.language or None)
            elif step.id == "package_manager":
                self.result.package_manager = method(self.result.language or None)

        return self.result

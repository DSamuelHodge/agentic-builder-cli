"""Project template selection for interactive mode."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from prompt_toolkit.completion import WordCompleter
except Exception:  # pragma: no cover
    WordCompleter = None


@dataclass
class ProjectTemplate:
    id: str
    name: str
    description: str
    language: str
    features: list[str]
    package_manager: str | None = None


TEMPLATES = [
    ProjectTemplate(
        id="py-minimal",
        name="Python Minimal",
        description="Bare-bones Python project",
        language="py",
        features=["basic-structure"],
    ),
    ProjectTemplate(
        id="py-api",
        name="Python API",
        description="FastAPI + Docker",
        language="py",
        features=["fastapi", "docker", "git"],
        package_manager="uv",
    ),
    ProjectTemplate(
        id="ts-minimal",
        name="TypeScript Minimal",
        description="Basic TS project",
        language="ts",
        features=["basic-structure"],
    ),
]


class TemplateSelector:
    def __init__(self):
        self.templates = {t.id: t for t in TEMPLATES}

    def prompt_template(self, language: str | None = None) -> ProjectTemplate:
        available = (
            [t for t in TEMPLATES if t.language == language] if language else TEMPLATES
        )
        choices = {t.id: t.name for t in available}

        if WordCompleter is not None:
            wc = WordCompleter(
                list(choices.keys()), meta_dict=choices, ignore_case=True
            )
            from prompt_toolkit import prompt

            while True:
                result = (
                    prompt(
                        "Select template: ", completer=wc, complete_while_typing=True
                    )
                    .strip()
                    .lower()
                )
                if result in self.templates:
                    return self.templates[result]
                print("Choose a valid template")
        else:
            # Fallback: print choices and ask simple input
            print("Available templates:")
            for t in available:
                print(f"  {t.id} - {t.name}: {t.description}")
            while True:
                result = input("Select template: ").strip().lower()
                if result in self.templates:
                    return self.templates[result]
                print("Invalid choice; try again")

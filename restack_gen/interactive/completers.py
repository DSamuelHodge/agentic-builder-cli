"""Completer helpers for interactive prompts.

Provide small helper classes that wrap prompt_toolkit completers.
If prompt_toolkit is not installed the classes provide lists of choices
for fallback suggestions.
"""

from __future__ import annotations

try:
    from prompt_toolkit.completion import Completer, Completion
except Exception:  # pragma: no cover
    Completer = object
    Completion = None


class ChoiceCompleter(Completer):
    def __init__(self, choices: dict[str, str] | list[str]):
        if isinstance(choices, dict):
            self.choices = choices
        else:
            self.choices = {c: c for c in choices}

    def get_completions(
        self, document, complete_event
    ):  # pragma: no cover - requires prompt_toolkit
        text = document.text_before_cursor.lower()
        for key, desc in self.choices.items():
            if key.startswith(text):
                yield Completion(key, start_position=-len(text), display=desc)


class PackageManagerCompleter(ChoiceCompleter):
    def __init__(self, language: str | None = None):
        pm_choices = {
            "uv": "uv — Unchecked Package Manager (Python)",
            "pip": "pip — Python's pip",
            "pnpm": "pnpm — Fast JS package manager",
            "npm": "npm — Node package manager",
        }
        if language == "py":
            valid = {k: v for k, v in pm_choices.items() if k in ("uv", "pip")}
        elif language == "ts":
            valid = {k: v for k, v in pm_choices.items() if k in ("pnpm", "npm")}
        else:
            valid = pm_choices
        super().__init__(valid)

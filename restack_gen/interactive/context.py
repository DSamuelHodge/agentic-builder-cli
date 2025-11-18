"""Context-aware defaults for interactive mode (user preferences)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class UserContext:
    CONFIG_FILE = Path.home() / ".config" / "restack-gen" / "preferences.json"

    def __init__(self):
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> dict:
        if not self.CONFIG_FILE.exists():
            return {}
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_preferences(self, prefs: dict) -> None:
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2)
        except Exception:
            pass

    def get_default_language(self) -> str | None:
        return self.preferences.get("default_language")

    def get_default_package_manager(self, language: str) -> str | None:
        return self.preferences.get("package_managers", {}).get(language)

    def update_from_result(self, result) -> None:
        self.preferences["default_language"] = result.language
        if "package_managers" not in self.preferences:
            self.preferences["package_managers"] = {}
        self.preferences["package_managers"][result.language] = result.package_manager
        self.save_preferences(self.preferences)

    def detect_project_context(self) -> dict:
        cwd = Path.cwd()
        context = {}
        if (cwd / "pyproject.toml").exists():
            context["detected_language"] = "py"
        elif (cwd / "package.json").exists():
            context["detected_language"] = "ts"

        if (cwd / "uv.lock").exists():
            context["detected_pm"] = "uv"
        elif (cwd / "pnpm-lock.yaml").exists():
            context["detected_pm"] = "pnpm"
        elif (cwd / "package-lock.json").exists():
            context["detected_pm"] = "npm"

        return context

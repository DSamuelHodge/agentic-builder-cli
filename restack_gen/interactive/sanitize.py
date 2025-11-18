"""Input sanitization utilities."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path


class InputSanitizer:
    @staticmethod
    def sanitize_project_name(name: str) -> str:
        name = "".join(char for char in name if unicodedata.category(char)[0] != "C")
        name = name.strip()
        name = re.sub(r"\s+", "-", name)
        name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
        if name and not re.match(r"^[a-zA-Z_]", name):
            name = f"_{name}"
        return name

    @staticmethod
    def sanitize_path(path: str) -> str:
        path = path.replace("\x00", "")
        try:
            return str(Path(path).expanduser().resolve())
        except Exception:
            return path

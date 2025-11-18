"""Fallback checks for interactive environment."""

from __future__ import annotations

import sys
import importlib.util as importlib_util


def can_use_interactive() -> tuple[bool, str | None]:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return False, "Not running in a terminal (TTY required)"

    try:
        if importlib_util.find_spec("prompt_toolkit") is None:
            return False, "prompt-toolkit not installed"
    except Exception:
        return False, "prompt-toolkit not installed"

    return True, None


def suggest_alternative() -> str:
    return "Use the standard CLI: restack-gen new <name> --help"

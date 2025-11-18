"""Styling helpers for interactive mode.

This module uses prompt_toolkit Style when available and falls back to
strings otherwise.
"""

from __future__ import annotations

try:
    from prompt_toolkit.styles import Style
except Exception:  # pragma: no cover - only affects environments w/o prompt_toolkit
    Style = None

COLORS = {
    "primary": "#00aa00",
    "secondary": "#00ffff",
    "accent": "#ffaa00",
    "muted": "#888888",
    "error": "#ff0000",
    "warning": "#ffff00",
}

if Style is not None:
    INTERACTIVE_STYLE = Style.from_dict(
        {
            "prompt": f"{COLORS['primary']} bold",
            "question": f"{COLORS['primary']}",
            "answer": f"{COLORS['secondary']}",
            "input": f"{COLORS['secondary']}",
            "instruction": f"{COLORS['muted']} italic",
            "hint": f"{COLORS['muted']}",
            "completion-menu": "bg:#262626 #ffffff",
            "completion-menu.completion": "bg:#262626 #ffffff",
            "completion-menu.completion.current": f"bg:{COLORS['primary']} #000000",
            "completion-menu.meta": f"bg:#262626 {COLORS['muted']}",
            "validation-error": f"{COLORS['error']} bold",
            "warning": f"{COLORS['warning']} bold",
            "success": f"{COLORS['primary']} bold",
        }
    )
else:
    INTERACTIVE_STYLE = None

SYMBOLS = {
    "prompt": "❯",
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "arrow": "→",
    "bullet": "•",
}


def get_prompt_prefix(text: str = "") -> str:
    return f"{SYMBOLS['prompt']} {text}" if text else SYMBOLS["prompt"]

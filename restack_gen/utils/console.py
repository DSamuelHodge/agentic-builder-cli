# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
import sys
import locale
from typing import Optional


from rich.console import Console

console = Console()


class Color:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    @classmethod
    def disable(cls):
        """Disable colors for piped output."""
        for attr in [
            "RED",
            "GREEN",
            "YELLOW",
            "BLUE",
            "MAGENTA",
            "CYAN",
            "RESET",
            "BOLD",
        ]:
            setattr(cls, attr, "")


def _get_safe_icon(icon: str, fallback: str) -> str:
    """Get icon if encoding supports it, otherwise fallback."""
    enc = sys.stdout.encoding or locale.getpreferredencoding(False) or "utf-8"
    try:
        icon.encode(enc)
        return icon
    except Exception:
        return fallback


def print_error(message: str, hint: Optional[str] = None):
    """Print error message with optional hint."""
    err_icon = _get_safe_icon("✗", "X")
    hint_icon = _get_safe_icon("💡", "Hint")
    print(f"{Color.RED}{err_icon} Error:{Color.RESET} {message}")
    if hint:
        print(f"{Color.YELLOW}{hint_icon} Hint:{Color.RESET} {hint}")


def print_success(message: str):
    """Print success message."""
    ok = _get_safe_icon("✓", "OK")
    print(f"{Color.GREEN}{ok}{Color.RESET} {message}")


def print_warning(message: str):
    """Print warning message."""
    warn = _get_safe_icon("⚠", "!")
    print(f"{Color.YELLOW}{warn}{Color.RESET} {message}")


def print_info(message: str):
    """Print info message."""
    info = _get_safe_icon("ℹ", "i")
    print(f"{Color.CYAN}{info}{Color.RESET} {message}")


def confirm(message: str, default: bool = False) -> bool:
    """Prompt user for confirmation."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(message + suffix).strip().lower()
    return response in ("y", "yes") if response else default

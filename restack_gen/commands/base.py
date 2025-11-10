# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from abc import ABC, abstractmethod


class Command(ABC):
    """Base class for CLI commands."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def execute(self, args: list[str]) -> int:
        """Execute command. Returns exit code (0 for success)."""
        pass

    def log(self, message: str, level: str = "info"):
        """Log message if not in quiet mode."""
        if self.config.quiet and level == "info":
            return
        from ..utils.console import (
            print_error,
            print_warning,
            print_success,
            print_info,
        )

        log_funcs = {
            "error": print_error,
            "warning": print_warning,
            "success": print_success,
            "info": print_info,
        }
        log_funcs.get(level, print_info)(message)

    def dry_run_log(self, message: str):
        """Log action in dry-run mode."""
        if self.config.dry_run:
            from ..utils.console import Color

            print(f"{Color.CYAN}[DRY RUN]{Color.RESET} {message}")

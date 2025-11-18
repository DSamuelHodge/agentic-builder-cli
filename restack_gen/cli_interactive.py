"""Interactive CLI mode for restack-gen.

This is a minimal interactive mode that guides the user through
project creation. It uses prompt_toolkit if available, otherwise falls
back to built-in input().
"""
from __future__ import annotations

import sys
from enum import IntEnum
from typing import Sequence

from .constants import Config, Language
from .utils.console import print_error, print_info, print_success


class ExitCode(IntEnum):
    SUCCESS = 0
    ERROR = 1
    INTERRUPTED = 130


class InteractiveCLI:
    """Simple interactive CLI controller.

    This implementation is intentionally small and uses the existing
    commands (e.g., `new`) to perform the actual work.
    """

    def __init__(self, argv: Sequence[str] | None = None):
        self.argv = list(argv or [])
        self.config = self._parse_minimal_args(self.argv)

    def _parse_minimal_args(self, argv: Sequence[str]) -> Config:
        import argparse

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-v", "--verbose", action="store_true")
        parser.add_argument("-q", "--quiet", action="store_true")
        parser.add_argument("--no-color", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("-y", "--yes", action="store_true")
        parser.add_argument("-i", "--interactive", action="store_true")
        parser.add_argument("--cwd", type=str, help="Working directory")

        args, _ = parser.parse_known_args(argv)

        from .constants import Config, Language
        from pathlib import Path

        lang = None
        return Config(
            lang=lang,
            package_manager=None,
            cwd=Path(args.cwd) if args.cwd else None,
            quiet=args.quiet,
            yes=args.yes,
            force=False,
            dry_run=args.dry_run,
            verbose=args.verbose,
            no_color=args.no_color,
        )

    def _use_prompt_toolkit(self) -> bool:
        try:
            import prompt_toolkit  # type: ignore

            return True
        except Exception:
            return False

    def _prompt(self, message: str, default: str | None = None) -> str:
        if self._use_prompt_toolkit():
            from prompt_toolkit import prompt

            prompt_message = f"{message} " if default is None else f"{message} [{default}] "
            result = prompt(prompt_message)
            if not result and default is not None:
                return default
            return result
        else:
            if default is not None:
                result = input(f"{message} [{default}] ")
                if not result:
                    return default
                return result
            return input(f"{message} ")

    def _choose_language(self) -> Language:
        if self.config.lang:
            return self.config.lang

        result = self._prompt("Programming language (py/ts)", "py").strip().lower()
        if result not in ("py", "ts"):
            print_info("Please choose 'py' or 'ts'. Defaulting to 'py'.")
            return Language.PYTHON
        return Language.PYTHON if result == "py" else Language.TYPESCRIPT

    def run(self) -> int:
        try:
            print_success("🚀 Welcome to restack-gen (interactive mode)")

            action = self._prompt("What would you like to do? (new/help/exit)", "new").strip().lower()

            if action == "new":
                return self._handle_new()
            if action == "help":
                from .commands.info import HelpCommand

                HelpCommand(self.config).execute([])
                return ExitCode.SUCCESS

            return ExitCode.SUCCESS

        except KeyboardInterrupt:
            print_info("\n\n👋 Goodbye!")
            return ExitCode.INTERRUPTED

        except Exception as e:
            print_error(f"Unexpected error: {e}")
            if self.config.verbose:
                import traceback

                traceback.print_exc()
            return ExitCode.ERROR

    def _handle_new(self) -> int:
        """Launch interactive session to collect project options and create project."""
        # import interactive session here so tests can patch the class at
        # `restack_gen.interactive.InteractiveSession`
        from .interactive import InteractiveSession
        from .commands.new import NewCommand

        session = InteractiveSession(self.config)
        try:
            result = session.start()
        except KeyboardInterrupt:
            print_info("Project creation cancelled")
            return ExitCode.INTERRUPTED

        # Map result to config
        if result.language == "py":
            self.config.lang = Language.PYTHON
        else:
            self.config.lang = Language.TYPESCRIPT

        self.config.package_manager = result.package_manager
        if result.working_directory:
            from pathlib import Path

            self.config.cwd = Path(result.working_directory)

        # If not auto-confirmed, ask the user
        if not self.config.yes:
            confirm = self._prompt(f"Create project '{result.project_name}'? (y/N)", "N").strip().lower()
            if confirm not in ("y", "yes"):
                print_info("Cancelled by user")
                return ExitCode.SUCCESS

        cmd = NewCommand(self.config)
        return cmd.execute([result.project_name])


def main(argv: Sequence[str] | None = None) -> int:
    cli = InteractiveCLI(argv)
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
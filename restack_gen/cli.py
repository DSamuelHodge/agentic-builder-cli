"""Command-line interface for restack-gen.

This module provides the main entry point and argument parsing for the
restack-gen code generator tool.
"""

from __future__ import annotations

import argparse
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING

from .commands import CommandRegistry
from .constants import Config, Language
from .utils.console import Color, print_error, print_info, print_success

if TYPE_CHECKING:
    from collections.abc import Sequence


class ExitCode(IntEnum):
    """Standard exit codes for the CLI."""

    SUCCESS = 0
    ERROR = 1
    INTERRUPTED = 130


class ConcurrentProjectCreator:
    """Handles concurrent creation of multiple projects."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def create_projects(self, project_names: Sequence[str]) -> int:
        """Create multiple projects concurrently.

        Args:
            project_names: List of project names to create.

        Returns:
            Exit code (0 for success, 1 for any failures).
        """
        if not project_names:
            print_error("No project names provided for concurrent creation")
            return ExitCode.ERROR

        results: dict[str, int] = {}

        with ThreadPoolExecutor() as executor:
            future_to_name = {
                executor.submit(self._create_single_project, name): name
                for name in project_names
            }

            total = len(project_names)
            completed = 0

            for future in as_completed(future_to_name):
                completed += 1
                name = future_to_name[future]

                try:
                    result_name, exit_code = future.result()
                    results[result_name] = exit_code
                    status = "✓" if exit_code == ExitCode.SUCCESS else "✗"

                    if not self.config.quiet:
                        print_info(f"[{completed}/{total}] {status} {result_name}")

                except Exception as e:
                    results[name] = ExitCode.ERROR
                    if not self.config.quiet:
                        print_info(f"[{completed}/{total}] ✗ {name}")
                    if self.config.verbose:
                        print_error(f"Error creating {name}: {e}")

        return self._report_results(results)

    def _create_single_project(self, name: str) -> tuple[str, int]:
        """Create a single project and handle cleanup on failure.

        Args:
            name: Project name to create.

        Returns:
            Tuple of (project_name, exit_code).
        """
        from .commands.new import NewCommand

        cmd = NewCommand(self.config)

        try:
            exit_code = cmd.execute([name])

            if exit_code != ExitCode.SUCCESS:
                self._cleanup_failed_project(cmd, name)

            return (name, exit_code)

        except Exception as e:
            if self.config.verbose:
                print_error(f"Exception while creating {name}: {e}")
                traceback.print_exc()

            self._cleanup_failed_project(cmd, name)
            return (name, ExitCode.ERROR)

    def _cleanup_failed_project(self, cmd: "NewCommand", name: str) -> None:
        """Clean up project directory after creation failure.

        Args:
            cmd: NewCommand instance.
            name: Project name.
        """
        import shutil

        try:
            # TODO: This accesses a private method - should be refactored
            # Consider making get_app_directory public or handling cleanup
            # inside NewCommand itself
            app_dir = cmd._get_app_directory(name)
            if app_dir.exists():
                shutil.rmtree(app_dir, ignore_errors=True)
        except Exception as e:
            if self.config.verbose:
                print_error(f"Failed to cleanup {name}: {e}")

    def _report_results(self, results: dict[str, int]) -> int:
        """Report final results and return appropriate exit code.

        Args:
            results: Dictionary mapping project names to exit codes.

        Returns:
            Exit code (0 if all succeeded, 1 if any failed).
        """
        successful = [name for name, code in results.items() if code == ExitCode.SUCCESS]
        failed = [name for name, code in results.items() if code != ExitCode.SUCCESS]

        if failed:
            print_error(f"Failed to create: {', '.join(failed)}")
            if successful and not self.config.quiet:
                print_info(f"Successfully created: {', '.join(successful)}")
            return ExitCode.ERROR

        if not self.config.quiet:
            print_success(f"All projects created successfully: {', '.join(successful)}")

        return ExitCode.SUCCESS


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="restack-gen",
        description="Restack code generator - Create and manage code projects",
        add_help=False,
        epilog="Run 'restack-gen help' for detailed usage information",
    )

    # Positional arguments
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run (e.g., new, help)",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments for the command",
    )

    # Special commands
    parser.add_argument(
        "--concurrent-new",
        nargs="*",
        metavar="NAME",
        help="Create multiple projects concurrently",
    )

    # Configuration options
    parser.add_argument(
        "--lang",
        choices=["py", "ts"],
        help="Programming language (Python or TypeScript)",
    )
    parser.add_argument(
        "--pm",
        choices=["uv", "pip", "pnpm", "npm"],
        help="Package manager to use",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        metavar="PATH",
        help="Working directory for operations",
    )

    # Behavior flags
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing files/directories",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically confirm all prompts",
    )

    # Output control
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    # Help
    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="Show help message",
    )

    return parser


def build_config(args: argparse.Namespace) -> Config:
    """Build configuration object from parsed arguments.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Config instance with settings from arguments.
    """
    return Config(
        lang=Language(args.lang) if args.lang else None,
        package_manager=args.pm,
        cwd=args.cwd,
        quiet=args.quiet,
        yes=args.yes,
        force=args.force,
        dry_run=args.dry_run,
        verbose=args.verbose,
        no_color=args.no_color,
    )


def handle_concurrent_new(
    project_names: Sequence[str],
    config: Config,
) -> int:
    """Handle concurrent project creation.

    Args:
        project_names: List of project names to create.
        config: Configuration object.

    Returns:
        Exit code.
    """
    creator = ConcurrentProjectCreator(config)
    return creator.create_projects(project_names)


def execute_command(command_name: str, args: list[str], config: Config) -> int:
    """Execute a single command.

    Args:
        command_name: Name of the command to execute.
        args: Arguments to pass to the command.
        config: Configuration object.

    Returns:
        Exit code from command execution.
    """
    registry = CommandRegistry(config)
    command = registry.get(command_name)

    if command is None:
        print_error(
            f"Unknown command: {command_name}",
            hint="Run 'restack-gen help' for usage",
        )
        return ExitCode.ERROR

    return command.execute(args)


def show_help() -> int:
    """Display help information.

    Returns:
        Exit code (always SUCCESS).
    """
    from .commands.info import HelpCommand

    HelpCommand(Config()).execute([])
    return ExitCode.SUCCESS


def configure_output(args: argparse.Namespace) -> None:
    """Configure output settings based on arguments.

    Args:
        args: Parsed command-line arguments.
    """
    if args.no_color or not sys.stdout.isatty():
        Color.disable()


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Configure output
    configure_output(args)

    try:
        # Handle concurrent project creation
        if args.concurrent_new is not None:
            config = build_config(args)
            return handle_concurrent_new(args.concurrent_new, config)

        # Show help if requested or no command given
        if args.help or not args.command:
            return show_help()

        # Execute single command
        config = build_config(args)
        return execute_command(args.command, args.args, config)

    except KeyboardInterrupt:
        print("\n\nCancelled by user", file=sys.stderr)
        return ExitCode.INTERRUPTED

    except Exception as e:
        print_error(f"Unexpected error: {e}")

        if args.verbose:
            traceback.print_exc()

        return ExitCode.ERROR


if __name__ == "__main__":
    sys.exit(main())
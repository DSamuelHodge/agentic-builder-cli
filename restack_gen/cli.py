# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
import argparse
import sys
from pathlib import Path

from .constants import Config, Language
from .utils.console import Color, print_error
from .commands import CommandRegistry


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="restack-gen",
        description="Restack code generator",
        add_help=False,
    )
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs="*", help="Command arguments")
    # Add concurrent-new subcommand for concurrent project generation
    parser.add_argument("--concurrent-new", nargs="*", help="Create multiple projects concurrently (provide names)")
    parser.add_argument("--lang", choices=["py", "ts"])
    parser.add_argument("--pm", choices=["uv", "pip", "pnpm", "npm"])
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    return parser


def build_config(args) -> Config:
    """Build configuration from parsed arguments."""
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


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    # Disable colors if needed
    if args.no_color or not sys.stdout.isatty():
        Color.disable()
    # Handle concurrent-new subcommand FIRST
    if args.concurrent_new:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from .commands.new import NewCommand
        import shutil
        from .utils.console import print_success
        config = build_config(args)
        results = {}
        def run_new(name):
            cmd = NewCommand(config)
            try:
                code = cmd.execute([name])
                if code != 0:
                    # Cleanup on failure
                    app_dir = cmd._get_app_directory(name)
                    if app_dir.exists():
                        shutil.rmtree(app_dir, ignore_errors=True)
                return (name, code)
            except Exception as e:
                app_dir = cmd._get_app_directory(name)
                if app_dir.exists():
                    shutil.rmtree(app_dir, ignore_errors=True)
                return (name, 1)
        with ThreadPoolExecutor() as executor:
            future_to_name = {executor.submit(run_new, name): name for name in args.concurrent_new}
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    name, code = future.result()
                    results[name] = code
                except Exception:
                    results[name] = 1
        failed = [n for n, c in results.items() if c != 0]
        if failed:
            print_error(f"Failed to create: {', '.join(failed)}")
            return 1
        print_success(f"All projects created successfully: {', '.join(results.keys())}")
        return 0
    # Show help if needed
    if args.help or not args.command:
        from .commands.info import HelpCommand
        HelpCommand(Config()).execute([])
        return 0
    # Build config and get command
    config = build_config(args)
    registry = CommandRegistry(config)
    command = registry.get(args.command)
    if command is None:
        print_error(
            f"Unknown command: {args.command}", hint="Run 'restack-gen help' for usage"
        )
        return 1
    # Execute
    try:
        return command.execute(args.args)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if config.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

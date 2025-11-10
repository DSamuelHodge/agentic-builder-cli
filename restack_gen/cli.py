import argparse
import sys
from pathlib import Path
from typing import Optional

from .constants import Config, Language, VERSION
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
	parser.add_argument("args", nargs=argparse.REMAINDER, help="Command arguments")
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
			f"Unknown command: {args.command}",
			hint=f"Run 'restack-gen help' for usage"
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

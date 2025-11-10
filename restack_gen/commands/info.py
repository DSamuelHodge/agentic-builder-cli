from pathlib import Path
from .base import Command
from ..constants import VERSION, Language, GenerationType
from ..utils.console import Color, print_error, print_warning

class VersionCommand(Command):
	"""Show version information."""
	def execute(self, args: list[str]) -> int:
		print(f"restack-gen version {VERSION}")
		return 0

class ListTemplatesCommand(Command):
	"""List available templates."""
	def execute(self, args: list[str]) -> int:
		templates_root = Path(__file__).parent.parent.parent / "templates"
		if not templates_root.exists():
			print_warning("Templates directory not found")
			return 1
		if self.config.lang:
			return self._show_language_templates(templates_root, self.config.lang)
		else:
			return self._show_all_templates(templates_root)
	def _show_language_templates(self, templates_root: Path, lang: Language) -> int:
		"""Show templates for specific language."""
		lang_dir = templates_root / lang.value
		if not lang_dir.exists():
			print_error(f"No templates for language: {lang.value}")
			return 1
		templates = self._get_templates(lang_dir)
		print(f"{Color.BOLD}Templates ({lang.value}):{Color.RESET}")
		for t in sorted(templates):
			print(f"  • {t}")
		return 0
	def _show_all_templates(self, templates_root: Path) -> int:
		"""Show all templates organized by language."""
		print(f"{Color.BOLD}Available Templates:{Color.RESET}\n")
		for lang_dir in sorted(templates_root.iterdir()):
			if not lang_dir.is_dir() or lang_dir.name.startswith('.'):
				continue
			templates = self._get_templates(lang_dir)
			if templates:
				print(f"{Color.CYAN}{lang_dir.name}:{Color.RESET}")
				for t in sorted(templates):
					print(f"  • {t}")
				print()
		return 0
	def _get_templates(self, directory: Path) -> list[str]:
		"""Get list of template files in directory."""
		return [
			p.name for p in directory.iterdir()
			if p.is_file() and not p.name.startswith('.')
		]

class HelpCommand(Command):
	"""Show help information."""
	def execute(self, args: list[str]) -> int:
		print(self._get_help_text())
		return 0
	def _get_help_text(self) -> str:
		"""Generate help text."""
		return f"""{Color.BOLD}restack-gen{Color.RESET} - Restack code generator v{VERSION}

{Color.BOLD}USAGE:{Color.RESET}
  restack-gen <command> [options] [arguments]

{Color.BOLD}COMMANDS:{Color.RESET}
  {Color.CYAN}new{Color.RESET} <app_name>              Create a new Restack app
  {Color.CYAN}g{Color.RESET}, {Color.CYAN}generate{Color.RESET} <type> <name>  Generate code (agent|function|workflow)
  {Color.CYAN}routes{Color.RESET}                       List registered agents/workflows/functions
  {Color.CYAN}dev{Color.RESET}                          Start local engine and hot-reload
  {Color.CYAN}build{Color.RESET}                        Type check, lint, and package
  {Color.CYAN}test{Color.RESET} [args]                  Run tests with pytest
  {Color.CYAN}doctor{Color.RESET}                       Run environment diagnostics
  {Color.CYAN}list-templates{Color.RESET}               List available code templates
  {Color.CYAN}version{Color.RESET}                      Show version information
  {Color.CYAN}help{Color.RESET}                         Show this help message

{Color.BOLD}OPTIONS:{Color.RESET}
  --lang <py|ts>               Language (auto-detect if omitted)
  --pm <uv|pip|pnpm|npm>       Package manager preference
  --cwd <path>                 Run in a custom directory
  --force                      Overwrite existing files
  --dry-run                    Preview actions without executing
  -q, --quiet                  Reduce output verbosity
  -v, --verbose                Increase output verbosity
  -y, --yes                    Assume yes to all prompts
  --no-color                   Disable colored output
  -h, --help                   Show this help message

{Color.BOLD}EXAMPLES:{Color.RESET}
  # Create a new app
  restack-gen new my-app --lang py

  # Generate components
  restack-gen g agent EmailHandler
  restack-gen g function send_email
  restack-gen g workflow email_campaign

  # Development workflow
  restack-gen routes          # List all components
  restack-gen test            # Run tests
  restack-gen dev             # Start dev server

  # Dry run mode
  restack-gen g agent TestAgent --dry-run

{Color.BOLD}DOCUMENTATION:{Color.RESET}
  https://docs.restack.io
"""

# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from pathlib import Path
from .base import Command
from ..constants import VERSION, Language
from ..utils.console import Color, print_error, print_warning


class VersionCommand(Command):
    """Show version information."""

    def execute(self, args: list[str]) -> int:
        print(f"restack-gen version {VERSION}")
        return 0


class ListTemplatesCommand(Command):
    """List available templates."""

    def __init__(self, config, templates_root=None):
        super().__init__(config)
        self.templates_root = templates_root

    def execute(self, args: list[str]) -> int:
        templates_root = (
            self.templates_root or Path(__file__).parent.parent.parent / "templates"
        )
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
            if not lang_dir.is_dir() or lang_dir.name.startswith("."):
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
            p.name
            for p in directory.iterdir()
            if p.is_file() and not p.name.startswith(".")
        ]


class TelemetryCommand(Command):
    """Manage telemetry settings."""

    def execute(self, args: list[str]) -> int:
        if not args:
            self._show_status()
            return 0

        subcommand = args[0].lower()
        if subcommand == "enable":
            self._enable_telemetry()
        elif subcommand == "disable":
            self._disable_telemetry()
        else:
            print_error(f"Unknown telemetry subcommand: {subcommand}")
            print("Usage: restack-gen telemetry [enable|disable]")
            return 1
        return 0

    def _show_status(self):
        """Show current telemetry status."""
        from ..utils.telemetry import get_collector
        collector = get_collector()
        status = "enabled" if collector.is_enabled() else "disabled"
        print(f"Telemetry is currently {status}.")
        print("Use 'restack-gen telemetry enable' or 'restack-gen telemetry disable' to change.")

    def _enable_telemetry(self):
        """Enable telemetry."""
        from ..utils.telemetry import get_collector
        collector = get_collector()
        collector.enable()
        print_success("Telemetry enabled. Thank you for helping improve restack-gen!")

    def _disable_telemetry(self):
        """Disable telemetry."""
        from ..utils.telemetry import get_collector
        collector = get_collector()
        collector.disable()
        print_success("Telemetry disabled.")
    """Show help information."""

    def execute(self, args: list[str]) -> int:
        print(self._get_help_text())
        return 0

    def _get_help_text(self) -> str:
        """Generate help text."""
        return f"""{Color.BOLD}restack-gen{Color.RESET} - Restack code generator v{VERSION}

{Color.BOLD}USAGE:{Color.RESET}
  restack-gen <command> [options] [arguments]
  restack-gen -i                           # Interactive mode

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
  {Color.CYAN}telemetry{Color.RESET}                   Manage telemetry settings
  {Color.CYAN}help{Color.RESET}                         Show this help message

{Color.BOLD}OPTIONS:{Color.RESET}
  -i, --interactive            Launch interactive mode
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

  # Interactive mode for guided setup
  restack-gen -i
  restack-gen new -i

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

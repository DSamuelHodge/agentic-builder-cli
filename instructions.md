# Proposed modular structure for restack-gen CLI
# This shows how to break down the monolithic cli.py into focused modules

"""
restack_gen/
├── __init__.py
├── __main__.py              # Entry point
├── cli.py                   # Slim CLI setup and routing
├── config.py                # Configuration management
├── core/
│   ├── __init__.py
│   ├── project.py           # ProjectStructure
│   ├── templates.py         # TemplateEngine
│   └── validation.py        # Validator utilities
├── commands/
│   ├── __init__.py
│   ├── base.py              # Command abstract base
│   ├── new.py               # NewCommand
│   ├── generate.py          # GenerateCommand
│   ├── dev.py               # DevCommand
│   ├── routes.py            # RoutesCommand
│   ├── build.py             # BuildCommand
│   ├── test.py              # TestCommand
│   ├── doctor.py            # DoctorCommand
│   └── info.py              # VersionCommand, HelpCommand, ListTemplatesCommand
├── utils/
│   ├── __init__.py
│   ├── console.py           # Color, print functions
│   ├── text.py              # snake_case, pascal_case, etc.
│   └── toml.py              # TOMLLoader
└── constants.py             # VERSION, Language, GenerationType enums
"""

# ===========================================================================
# constants.py - All constants and enums
# ===========================================================================

from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VERSION = "0.2.0"


class Language(Enum):
    PYTHON = "py"
    TYPESCRIPT = "ts"


class GenerationType(Enum):
    AGENT = "agent"
    FUNCTION = "function"
    WORKFLOW = "workflow"


@dataclass
class Config:
    """Global configuration for the CLI."""
    lang: Optional[Language] = None
    package_manager: Optional[str] = None
    cwd: Optional[Path] = None
    quiet: bool = False
    yes: bool = False
    force: bool = False
    dry_run: bool = False
    verbose: bool = False
    no_color: bool = False


# ===========================================================================
# utils/console.py - Console output utilities
# ===========================================================================

import sys
import locale
from typing import Optional


class Color:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def disable(cls):
        """Disable colors for piped output."""
        for attr in ['RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'RESET', 'BOLD']:
            setattr(cls, attr, '')


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
    return response in ('y', 'yes') if response else default


# ===========================================================================
# utils/text.py - Text transformation utilities
# ===========================================================================

import re


def snake_case(name: str) -> str:
    """Convert string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    return ''.join(word.capitalize() for word in snake_case(name).split('_'))


def kebab_case(name: str) -> str:
    """Convert string to kebab-case."""
    return snake_case(name).replace('_', '-')


# ===========================================================================
# core/validation.py - Input validation
# ===========================================================================

from pathlib import Path
import keyword


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class Validator:
    """Validates user input."""
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """Validate identifier name. Returns (is_valid, error_message)."""
        if not name:
            return False, "Name cannot be empty"
        
        name_check = name.replace('-', '_')
        
        if not name_check.replace('_', '').isalnum():
            return False, f"'{name}' contains invalid characters"
        
        if name[0].isdigit():
            return False, "Name cannot start with a digit"
        
        if name.startswith('_'):
            return False, "Name should not start with underscore (convention)"
        
        if '-' not in name and keyword.iskeyword(name):
            return False, f"'{name}' is a Python keyword"
        
        return True, ""
    
    @staticmethod
    def validate_path(path: Path, must_exist: bool = False) -> tuple[bool, str]:
        """Validate path. Returns (is_valid, error_message)."""
        try:
            resolved = path.resolve()
            
            if must_exist and not resolved.exists():
                return False, f"Path does not exist: {path}"
            
            if '..' in str(path):
                return False, "Path contains suspicious '..' components"
            
            return True, ""
        except Exception as e:
            return False, f"Invalid path: {e}"


# ===========================================================================
# core/project.py - Project structure management
# ===========================================================================

from pathlib import Path
from typing import Optional


class ProjectStructure:
    """Handles project directory structure and paths."""
    
    def __init__(self, root: Optional[Path] = None):
        self.root = self._find_project_root(root or Path.cwd())
    
    def _find_project_root(self, start_path: Path) -> Path:
        """Find project root by looking for marker files."""
        current = start_path.resolve()
        markers = ['restack.toml', 'pyproject.toml', 'package.json']
        
        for _ in range(10):  # Limit depth
            for marker in markers:
                if (current / marker).exists():
                    return current
            
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        return start_path.resolve()
    
    @property
    def src_dir(self) -> Path:
        return self.root / "src"
    
    @property
    def tests_dir(self) -> Path:
        return self.root / "tests"
    
    @property
    def scripts_dir(self) -> Path:
        return self.root / "scripts"
    
    def get_subdir(self, subdir: str) -> Path:
        """Get subdirectory path under src/."""
        return self.src_dir / subdir
    
    def ensure_structure(self):
        """Create standard project structure."""
        dirs = [
            self.src_dir / "agents",
            self.src_dir / "functions",
            self.src_dir / "workflows",
            self.tests_dir,
            self.scripts_dir,
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)


# ===========================================================================
# core/templates.py - Template engine
# ===========================================================================

from pathlib import Path
from typing import Any, Optional


class TemplateEngine:
    """Handles template loading and rendering."""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self._env = None
    
    @property
    def env(self):
        """Get Jinja2 environment (lazy loaded)."""
        if self._env is None:
            try:
                from jinja2 import Environment, FileSystemLoader
                self._env = Environment(
                    loader=FileSystemLoader(str(self.templates_dir))
                )
            except ImportError:
                raise ImportError(
                    "Jinja2 is required for template rendering. "
                    "Install with: pip install jinja2"
                )
        return self._env
    
    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render template with context."""
        template = self.env.get_template(template_name)
        return template.render(context)
    
    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        return (self.templates_dir / template_name).exists()
    
    def list_templates(self) -> list[str]:
        """List all available templates."""
        if not self.templates_dir.exists():
            return []
        return [
            p.name
            for p in self.templates_dir.iterdir()
            if p.is_file() and not p.name.startswith('.')
        ]


def build_template_context(
    name: str,
    app_name: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Build unified template context."""
    from .text import snake_case, pascal_case, kebab_case
    
    app_name = app_name or name
    
    context = {
        'name': name,
        'app_name': app_name,
        'snake_name': snake_case(name),
        'pascal_name': pascal_case(name),
        'kebab_name': kebab_case(name),
        'snake_app_name': snake_case(app_name),
        'pascal_app_name': pascal_case(app_name),
        'kebab_app_name': kebab_case(app_name),
        # Defaults for TOML-derived variables
        'timeouts_start_to_close_seconds': 30,
        'timeouts_start_to_close': '30s',
        'retry_policies_default_json': '{}',
        'queues_default': 'default',
    }
    
    context.update(kwargs)
    return context


# ===========================================================================
# commands/base.py - Command base class
# ===========================================================================

from abc import ABC, abstractmethod
from typing import Optional


class Command(ABC):
    """Base class for CLI commands."""
    
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def execute(self, args: list[str]) -> int:
        """Execute command. Returns exit code (0 for success)."""
        pass
    
    def log(self, message: str, level: str = 'info'):
        """Log message if not in quiet mode."""
        if self.config.quiet and level == 'info':
            return
        
        from ..utils.console import (
            print_error, print_warning, print_success, print_info
        )
        
        log_funcs = {
            'error': print_error,
            'warning': print_warning,
            'success': print_success,
            'info': print_info,
        }
        
        log_funcs.get(level, print_info)(message)
    
    def dry_run_log(self, message: str):
        """Log action in dry-run mode."""
        if self.config.dry_run:
            from ..utils.console import Color
            print(f"{Color.CYAN}[DRY RUN]{Color.RESET} {message}")


# ===========================================================================
# commands/generate.py - Generate command (example of extracted command)
# ===========================================================================

from pathlib import Path
from .base import Command
from ..constants import GenerationType, Language
from ..core.project import ProjectStructure
from ..core.templates import TemplateEngine, build_template_context
from ..core.validation import Validator
from ..utils.console import print_error, print_success, confirm


class GenerateCommand(Command):
    """Generate code components."""
    
    def execute(self, args: list[str]) -> int:
        if len(args) < 2:
            print_error("Type and name required")
            print("Usage: restack-gen g <type> <name> [options]")
            return 1
        
        gen_type_str, gen_name = args[0], args[1]
        
        # Validate and execute
        gen_type = self._validate_type(gen_type_str)
        if not gen_type:
            return 1
        
        if not self._validate_name(gen_name):
            return 1
        
        return self._generate(gen_type, gen_name)
    
    def _validate_type(self, gen_type_str: str) -> Optional[GenerationType]:
        """Validate generation type."""
        try:
            return GenerationType(gen_type_str)
        except ValueError:
            types_list = ', '.join(t.value for t in GenerationType)
            print_error(
                f"Unknown type: {gen_type_str}",
                hint=f"Available types: {types_list}"
            )
            return None
    
    def _validate_name(self, name: str) -> bool:
        """Validate entity name."""
        is_valid, error = Validator.validate_name(name)
        if not is_valid:
            print_error(f"Invalid name: {error}")
        return is_valid
    
    def _generate(self, gen_type: GenerationType, gen_name: str) -> int:
        """Perform the generation."""
        try:
            project = ProjectStructure(self.config.cwd)
            lang = self._detect_language(project)
            engine = self._setup_engine(lang)
            
            output_file = self._get_output_path(project, gen_type, gen_name, lang)
            
            if not self._check_overwrite(output_file):
                return 0
            
            if self.config.dry_run:
                self.dry_run_log(f"Would generate {gen_type.value}: {output_file}")
                return 0
            
            # Render and write
            context = build_template_context(gen_name, app_name=project.root.name)
            template_name = f"{gen_type.value}.{lang.value}.j2"
            content = engine.render(template_name, context)
            
            output_file.write_text(content, encoding='utf-8')
            print_success(f"Generated {gen_type.value}: {output_file}")
            
            return 0
            
        except Exception as e:
            print_error(f"Failed to generate code: {e}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _detect_language(self, project: ProjectStructure) -> Language:
        """Detect project language from files."""
        if self.config.lang:
            return self.config.lang
        
        if list(project.src_dir.glob("**/*.py")):
            return Language.PYTHON
        if list(project.src_dir.glob("**/*.ts")):
            return Language.TYPESCRIPT
        
        return Language.PYTHON
    
    def _setup_engine(self, lang: Language) -> TemplateEngine:
        """Setup template engine for language."""
        templates_root = Path(__file__).parent.parent.parent / "templates"
        template_dir = templates_root / lang.value
        
        if not template_dir.exists():
            raise FileNotFoundError(f"No templates found for {lang.value}")
        
        return TemplateEngine(template_dir)
    
    def _get_output_path(
        self,
        project: ProjectStructure,
        gen_type: GenerationType,
        gen_name: str,
        lang: Language
    ) -> Path:
        """Get output file path."""
        from ..utils.text import snake_case
        
        subdir_map = {
            GenerationType.AGENT: "agents",
            GenerationType.FUNCTION: "functions",
            GenerationType.WORKFLOW: "workflows",
        }
        
        output_dir = project.get_subdir(subdir_map[gen_type])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return output_dir / f"{snake_case(gen_name)}.{lang.value}"
    
    def _check_overwrite(self, output_file: Path) -> bool:
        """Check if file can be overwritten."""
        if not output_file.exists():
            return True
        
        if self.config.force:
            return True
        
        if self.config.yes:
            return False
        
        return confirm(f"File {output_file.name} already exists. Overwrite?")


# ===========================================================================
# utils/toml.py - TOML handling
# ===========================================================================

from pathlib import Path
from typing import Any, Optional


class TOMLLoader:
    """Handles TOML file loading with fallback support."""
    
    _lib = None
    _checked = False
    
    @classmethod
    def _get_lib(cls):
        """Get TOML library with caching."""
        if cls._checked:
            return cls._lib
        
        cls._checked = True
        try:
            import tomllib
            cls._lib = ('tomllib', tomllib)
        except ImportError:
            try:
                import toml
                cls._lib = ('toml', toml)
            except ImportError:
                cls._lib = None
        
        return cls._lib
    
    @classmethod
    def load(cls, path: Path) -> dict[str, Any]:
        """Load TOML file."""
        if not path.exists():
            raise FileNotFoundError(f"TOML file not found: {path}")
        
        lib = cls._get_lib()
        if lib is None:
            raise ValueError(
                "No TOML library available. Install with: pip install tomli"
            )
        
        lib_name, lib_module = lib
        
        try:
            if lib_name == 'tomllib':
                with open(path, 'rb') as f:
                    return lib_module.load(f)
            else:
                return lib_module.load(path)
        except Exception as e:
            raise ValueError(f"Failed to parse TOML: {e}")
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if TOML library is available."""
        return cls._get_lib() is not None


# ===========================================================================
# commands/__init__.py - Command registry
# ===========================================================================

from typing import Optional, Dict, Type
from .base import Command
from ..constants import Config


class CommandRegistry:
    """Registry of all available commands."""
    
    def __init__(self, config: Config):
        self.config = config
        self._commands: Dict[str, Type[Command]] = {}
        self._register_commands()
    
    def _register_commands(self):
        """Register all available commands."""
        from .new import NewCommand
        from .generate import GenerateCommand
        from .routes import RoutesCommand
        from .dev import DevCommand
        from .build import BuildCommand
        from .test import TestCommand
        from .doctor import DoctorCommand
        from .info import VersionCommand, HelpCommand, ListTemplatesCommand
        
        self._commands = {
            'new': NewCommand,
            'g': GenerateCommand,
            'generate': GenerateCommand,
            'routes': RoutesCommand,
            'dev': DevCommand,
            'build': BuildCommand,
            'test': TestCommand,
            'doctor': DoctorCommand,
            'version': VersionCommand,
            'list-templates': ListTemplatesCommand,
            'ls-templates': ListTemplatesCommand,
            'help': HelpCommand,
        }
    
    def get(self, command: str) -> Optional[Command]:
        """Get command instance."""
        command_class = self._commands.get(command)
        if command_class:
            return command_class(self.config)
        return None
    
    def list_commands(self) -> list[str]:
        """List all unique command names."""
        seen = set()
        commands = []
        for name, cmd_class in self._commands.items():
            if cmd_class not in seen:
                commands.append(name)
                seen.add(cmd_class)
        return sorted(commands)


# ===========================================================================
# commands/new.py - New command (example showing helper methods)
# ===========================================================================

from pathlib import Path
import json
from .base import Command
from ..constants import Language, VERSION
from ..core.project import ProjectStructure
from ..core.templates import TemplateEngine, build_template_context
from ..core.validation import Validator
from ..utils.console import print_error, print_success, print_warning
from ..utils.text import snake_case, pascal_case
from ..utils.toml import TOMLLoader


class NewCommand(Command):
    """Create a new Restack app."""
    
    def execute(self, args: list[str]) -> int:
        if len(args) < 1:
            print_error("App name required")
            print("Usage: restack-gen new <app_name> [options]")
            return 1

        app_name = args[0]

        if not self._validate_app_name(app_name):
            return 1
        
        app_dir = self._get_app_directory(app_name)
        
        if app_dir.exists():
            print_error(
                f"Directory already exists: {app_dir}",
                hint="Choose a different name or remove the existing directory"
            )
            return 1
        
        if self.config.dry_run:
            self._show_dry_run(app_dir)
            return 0
        
        try:
            return self._create_app(app_name, app_dir)
        except Exception as e:
            print_error(f"Failed to create app: {e}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _validate_app_name(self, app_name: str) -> bool:
        """Validate application name."""
        is_valid, error = Validator.validate_name(app_name)
        if not is_valid:
            print_error(f"Invalid app name: {error}")
        return is_valid
    
    def _get_app_directory(self, app_name: str) -> Path:
        """Get application directory path."""
        base_dir = self.config.cwd or Path.cwd()
        return base_dir / app_name
    
    def _show_dry_run(self, app_dir: Path):
        """Show what would be created in dry-run mode."""
        self.dry_run_log(f"Would create directory: {app_dir}")
        self.dry_run_log("Would create project structure")
        self.dry_run_log("Would generate sample files")
    
    def _create_app(self, app_name: str, app_dir: Path) -> int:
        """Create the application."""
        project = ProjectStructure(app_dir)
        project.ensure_structure()
        self.log(f"Created directory structure at {app_dir}", 'success')
        
        lang = self.config.lang or Language.PYTHON
        engine, toml_values = self._setup_templates(app_name, app_dir, lang)
        
        self._create_readme(app_dir, app_name)
        self._generate_samples(engine, project, app_name, lang, toml_values)
        self._create_service(app_dir, app_name)
        self._create_run_script(project.scripts_dir)
        
        self._show_next_steps(app_name)
        return 0
    
    def _setup_templates(
        self,
        app_name: str,
        app_dir: Path,
        lang: Language
    ) -> tuple[TemplateEngine, dict]:
        """Setup template engine and load TOML config."""
        templates_root = Path(__file__).parent.parent.parent / "templates"
        template_dir = templates_root / lang.value
        
        if not template_dir.exists():
            print_warning(f"No templates found for {lang.value}, using minimal setup")
            template_dir = templates_root
        
        engine = TemplateEngine(template_dir)
        toml_values = self._load_toml_config(templates_root, app_name, app_dir)
        
        return engine, toml_values
    
    def _load_toml_config(
        self,
        templates_root: Path,
        app_name: str,
        app_dir: Path
    ) -> dict:
        """Load and parse TOML configuration."""
        toml_values = {}
        toml_template = templates_root / "restack.toml.j2"
        
        if not toml_template.exists():
            return toml_values
        
        try:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader(str(templates_root)))
            template = env.get_template("restack.toml.j2")
            output = template.render({"app_name": app_name})
            
            with open(app_dir / "restack.toml", "w", encoding="utf-8") as f:
                f.write(output)
            
            if TOMLLoader.is_available():
                data = TOMLLoader.load(app_dir / "restack.toml")
                toml_values = self._extract_toml_values(data)
        
        except Exception as e:
            if self.config.verbose:
                print_warning(f"Could not parse TOML: {e}")
        
        return toml_values
    
    def _extract_toml_values(self, data: dict) -> dict:
        """Extract values from parsed TOML data."""
        toml_values = {}
        
        # Extract timeouts
        timeouts = data.get("timeouts", {})
        start_to_close = timeouts.get("start_to_close")
        if isinstance(start_to_close, int):
            toml_values["timeouts_start_to_close_seconds"] = start_to_close
            toml_values["timeouts_start_to_close"] = f"{start_to_close}s"
        elif isinstance(start_to_close, str):
            toml_values["timeouts_start_to_close"] = start_to_close
        
        # Extract retry policies
        retry = data.get("retry_policies", {})
        toml_values["retry_policies_default_json"] = json.dumps(retry)
        
        # Extract queues
        queues = data.get("queues", {})
        toml_values["queues_default"] = queues.get("default", "default")
        
        return toml_values
    
    def _create_readme(self, app_dir: Path, app_name: str):
        """Create README file."""
        readme_content = f"""# {app_name}

Generated by restack-gen v{VERSION}

## Getting Started

```bash
# Start development server
restack-gen dev

# Generate new components
restack-gen g agent MyAgent
restack-gen g function my_function
restack-gen g workflow my_workflow

# Run tests
restack-gen test
```

## Project Structure

```
{app_name}/
├── src/
│   ├── agents/      # AI agents
│   ├── functions/   # Reusable functions
│   └── workflows/   # Workflow definitions
├── tests/           # Test files
├── scripts/         # Utility scripts
└── service.py       # Main service entry point
```
"""
        with open(app_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
    
    def _generate_samples(
        self,
        engine: TemplateEngine,
        project: ProjectStructure,
        app_name: str,
        lang: Language,
        toml_values: dict
    ):
        """Generate sample agent, function, and workflow."""
        ext = lang.value
        
        samples = [
            ("agent", f"agent.{ext}.j2", 
             project.get_subdir("agents") / f"{snake_case(app_name)}.{ext}", 
             app_name),
            ("function", f"function.{ext}.j2", 
             project.get_subdir("functions") / f"llm_chat.{ext}", 
             "llm_chat"),
            ("workflow", f"workflow.{ext}.j2", 
             project.get_subdir("workflows") / f"automated_workflow.{ext}", 
             "automated_workflow"),
        ]
        
        for sample_type, template_name, output_path, entity_name in samples:
            if engine.template_exists(template_name):
                try:
                    context = build_template_context(
                        entity_name, 
                        app_name=app_name, 
                        **toml_values
                    )
                    content = engine.render(template_name, context)
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    self.log(f"Generated sample {sample_type}: {output_path.name}")
                except Exception as e:
                    print_warning(f"Could not generate sample {sample_type}: {e}")
    
    def _create_service(self, app_dir: Path, app_name: str):
        """Create service.py registrar."""
        service_code = f"""from restack_ai import Restack
from src.agents.{snake_case(app_name)} import {pascal_case(app_name)}

client = Restack()

async def main():
    await client.start_service(
        agents=[{pascal_case(app_name)}],
        workflows=[],
        functions=[]
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
"""
        with open(app_dir / "service.py", "w", encoding="utf-8") as f:
            f.write(service_code)
    
    def _create_run_script(self, scripts_dir: Path):
        """Create run_engine.sh script."""
        script_content = """#!/usr/bin/env bash
set -e

echo "Starting Restack engine..."
# Add your engine start command here
# docker-compose up -d
# or
# restack-engine start
"""
        script_path = scripts_dir / "run_engine.sh"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        try:
            script_path.chmod(0o755)
        except Exception:
            pass
    
    def _show_next_steps(self, app_name: str):
        """Show next steps to user."""
        print_success(f"Created new Restack app: {app_name}")
        print()
        print("Next steps:")
        print(f"  cd {app_name}")
        print(f"  restack-gen dev")


# ===========================================================================
# commands/routes.py - Routes command
# ===========================================================================

from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import Color, print_warning


class RoutesCommand(Command):
    """List registered agents, workflows, and functions."""
    
    def execute(self, args: list[str]) -> int:
        project = ProjectStructure(self.config.cwd)
        
        print(f"{Color.BOLD}Registered Routes:{Color.RESET}\n")
        
        agents = self._find_files(project, "**/agent*.py")
        workflows = self._find_files(project, "**/workflow*.py")
        functions = self._find_files(project, "**/function*.py")
        
        self._print_section("Agents", agents, project)
        self._print_section("Workflows", workflows, project)
        self._print_section("Functions", functions, project)
        
        if not (agents or workflows or functions):
            print_warning("No routes found in project")
        
        return 0
    
    def _find_files(self, project: ProjectStructure, pattern: str) -> list:
        """Find files matching pattern."""
        return list(project.src_dir.glob(pattern))
    
    def _print_section(self, title: str, files: list, project: ProjectStructure):
        """Print a section of files."""
        if files:
            print(f"{Color.CYAN}{title}:{Color.RESET}")
            for file in sorted(files):
                rel_path = file.relative_to(project.root)
                print(f"  • {rel_path}")
            print()


# ===========================================================================
# commands/dev.py - Dev command
# ===========================================================================

import subprocess
from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import print_error, print_info, print_warning


class DevCommand(Command):
    """Start development server."""
    
    def execute(self, args: list[str]) -> int:
        project = ProjectStructure(self.config.cwd)
        run_script = project.scripts_dir / "run_engine.sh"
        
        if not run_script.exists():
            print_warning("scripts/run_engine.sh not found")
            print("Create this script to start your local engine")
            return 1
        
        if self.config.dry_run:
            self.dry_run_log(f"Would execute: {run_script}")
            return 0
        
        try:
            print_info("Starting local engine...")
            result = subprocess.run([str(run_script)], cwd=project.root)
            return result.returncode
        except Exception as e:
            print_error(f"Failed to start dev server: {e}")
            return 1


# ===========================================================================
# commands/build.py - Build command
# ===========================================================================

import subprocess
from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import print_info, print_success, print_warning


class BuildCommand(Command):
    """Build and check the project."""
    
    CHECKS = [
        (["mypy", "src"], "Type checking"),
        (["ruff", "check", "src"], "Linting"),
        (["black", "--check", "src"], "Format checking"),
    ]
    
    def execute(self, args: list[str]) -> int:
        project = ProjectStructure(self.config.cwd)
        
        if self.config.dry_run:
            for _, name in self.CHECKS:
                self.dry_run_log(f"Would run {name}")
            return 0
        
        print_info("Running type check, lint, and format checks...")
        
        all_passed = True
        for cmd, name in self.CHECKS:
            if not self._run_check(cmd, name, project):
                all_passed = False
        
        return 0 if all_passed else 1
    
    def _run_check(self, cmd: list[str], name: str, project) -> bool:
        """Run a single check."""
        try:
            result = subprocess.run(
                cmd,
                cwd=project.root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success(f"{name} passed")
                return True
            else:
                print_warning(f"{name} failed")
                if self.config.verbose and result.stdout:
                    print(result.stdout)
                return False
        except FileNotFoundError:
            print_warning(f"{name} tool not found (skipping)")
            return True


# ===========================================================================
# commands/test.py - Test command
# ===========================================================================

import subprocess
from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import print_error, print_info


class TestCommand(Command):
    """Run tests."""
    
    def execute(self, args: list[str]) -> int:
        project = ProjectStructure(self.config.cwd)
        
        if self.config.dry_run:
            self.dry_run_log("Would run pytest")
            return 0
        
        print_info("Running tests...")
        
        try:
            result = subprocess.run(
                ["pytest", "tests"] + args,
                cwd=project.root
            )
            return result.returncode
        except FileNotFoundError:
            print_error(
                "pytest not found",
                hint="Install with: pip install pytest"
            )
            return 1


# ===========================================================================
# commands/doctor.py - Doctor command
# ===========================================================================

import subprocess
import sys
import os
from .base import Command
from ..utils.console import Color, print_success, print_warning, print_info
from ..utils.toml import TOMLLoader


class DoctorCommand(Command):
    """Run environment diagnostics."""
    
    def execute(self, args: list[str]) -> int:
        print(f"{Color.BOLD}Environment Diagnostics{Color.RESET}\n")
        
        self._check_docker()
        self._check_python()
        self._check_packages()
        self._check_toml_support()
        self._check_environment()
        
        return 0
    
    def _check_docker(self):
        """Check Docker availability."""
        try:
            subprocess.run(
                ["docker", "info"],
                capture_output=True,
                check=True
            )
            print_success("Docker is running")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print_warning("Docker not available or not running")
    
    def _check_python(self):
        """Check Python version."""
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print_info(f"Python version: {version}")
    
    def _check_packages(self):
        """Check required packages."""
        packages = ["jinja2", "restack_ai"]
        for pkg in packages:
            try:
                __import__(pkg)
                print_success(f"{pkg} installed")
            except ImportError:
                print_warning(f"{pkg} not installed")
    
    def _check_toml_support(self):
        """Check TOML support."""
        if TOMLLoader.is_available():
            print_success("TOML support available")
        else:
            print_warning("TOML support not available (install tomli)")
    
    def _check_environment(self):
        """Check environment variables and services."""
        print(f"\n{Color.BOLD}Environment Variables:{Color.RESET}")
        restack_host = os.environ.get("RESTACK_HOST", "http://localhost:5233")
        print(f"  RESTACK_HOST: {restack_host}")
        
        print(f"\n{Color.BOLD}Services:{Color.RESET}")
        print(f"  Dev UI: {restack_host}")


# ===========================================================================
# commands/info.py - Info commands (Version, Help, ListTemplates)
# ===========================================================================

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


# ===========================================================================
# cli.py - Slim CLI setup (main entry point)
# ===========================================================================

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
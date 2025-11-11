# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from typing import Optional
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

    def _validate_type(self, gen_type_str: str) -> "Optional[GenerationType]":
        """Validate generation type."""
        try:
            return GenerationType(gen_type_str)
        except ValueError:
            types_list = ", ".join(t.value for t in GenerationType)
            print_error(
                f"Unknown type: {gen_type_str}", hint=f"Available types: {types_list}"
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
            # Always use the provided --cwd (project root) as the base for ProjectStructure
            project_root = Path(self.config.cwd or Path.cwd())
            project = ProjectStructure(project_root)
            # Ensure per-project src/ structure exists
            project.ensure_structure()
            lang = self._detect_language(project)
            engine = self._setup_engine(lang)
            output_file = self._get_output_path(project, gen_type, gen_name, lang)
            if not self._check_overwrite(output_file):
                return 0
            if self.config.dry_run:
                self.dry_run_log(f"Would generate {gen_type.value}: {output_file}")
                return 0
            # Render and write
            context = build_template_context(gen_name, app_name=project_root.name)
            template_name = f"{gen_type.value}.{lang.value}.j2"
            content = engine.render(template_name, context)
            output_file.write_text(content, encoding="utf-8")
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
        lang: Language,
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

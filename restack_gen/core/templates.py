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
	from ..utils.text import snake_case, pascal_case, kebab_case
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

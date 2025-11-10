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

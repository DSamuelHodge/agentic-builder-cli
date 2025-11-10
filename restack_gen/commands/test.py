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

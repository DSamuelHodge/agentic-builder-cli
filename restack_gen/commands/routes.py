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

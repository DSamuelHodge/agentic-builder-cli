# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import Color, print_warning


class RoutesCommand(Command):
    """List registered agents, workflows, and functions."""

    def execute(self, args: list[str]) -> int:
        project = ProjectStructure(self.config.cwd)
        print(f"{Color.BOLD}Registered Routes:{Color.RESET}\n")
        service_path = project.root / "service.py"
        if service_path.exists():
            agents, workflows, functions = self._parse_service(service_path)
            self._print_list("Agents", agents)
            self._print_list("Workflows", workflows)
            self._print_list("Functions", functions)
            if not (agents or workflows or functions):
                print_warning("No routes found in project")
        else:
            print_warning("No routes found in project")
        return 0

    def _parse_service(self, service_path):
        """Parse service.py to extract registered components."""
        agents = []
        workflows = []
        functions = []
        try:
            with open(service_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Simple regex to find the lists
            import re
            agent_match = re.search(r'agents=\[([^\]]*)\]', content)
            workflow_match = re.search(r'workflows=\[([^\]]*)\]', content)
            function_match = re.search(r'functions=\[([^\]]*)\]', content)
            if agent_match:
                agents = [x.strip() for x in agent_match.group(1).split(',') if x.strip()]
            if workflow_match:
                workflows = [x.strip() for x in workflow_match.group(1).split(',') if x.strip()]
            if function_match:
                functions = [x.strip() for x in function_match.group(1).split(',') if x.strip()]
        except Exception:
            pass
        return agents, workflows, functions

    def _print_list(self, title: str, items: list):
        """Print a list of items."""
        if items:
            print(f"{Color.CYAN}{title}:{Color.RESET}")
            for item in items:
                print(f"  • {item}")
            print()

# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
import subprocess
from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import print_error, print_info


class RestackTestsCommand(Command):
    """Run tests."""

    def execute(self, args: list[str]) -> int:
        project = ProjectStructure(self.config.cwd)
        if self.config.dry_run:
            self.dry_run_log("Would run pytest")
            return 0
        print_info("Running tests...")
        try:
            result = subprocess.run(["pytest", "tests"] + args, cwd=project.root)
            return result.returncode
        except FileNotFoundError:
            print_error("pytest not found", hint="Install with: pip install pytest")
            return 1
        except Exception as e:
            print_error(f"Failed to run tests: {e}")
            return 1

# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
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
                cmd, cwd=project.root, capture_output=True, text=True
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

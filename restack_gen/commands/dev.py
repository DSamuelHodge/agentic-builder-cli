# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
import subprocess
from .base import Command
from ..core.project import ProjectStructure
from ..utils.console import print_error, print_info, print_warning


class DevCommand(Command):
    """Start development server."""

    def execute(self, args: list[str]) -> int:
        import sys
        import shutil
        project = ProjectStructure(self.config.cwd)
        run_script_sh = project.scripts_dir / "run_engine.sh"
        run_script_bat = project.scripts_dir / "run_engine.bat"
        script_to_run = None
        if sys.platform.startswith("win") and run_script_bat.exists():
            script_to_run = run_script_bat
        elif run_script_sh.exists():
            script_to_run = run_script_sh
        if not script_to_run:
            print_warning("No run_engine script found (scripts/run_engine.sh or scripts/run_engine.bat)")
            print("Create one of these scripts to start your local engine")
            return 1
        if self.config.dry_run:
            self.dry_run_log(f"Would execute: {script_to_run}")
            return 0
        try:
            print_info("Starting local engine...")
            if sys.platform.startswith("win") and script_to_run.suffix == ".bat":
                result = subprocess.run([str(script_to_run)], cwd=project.root, shell=True)
                return result.returncode
            elif sys.platform.startswith("win") and script_to_run.suffix == ".sh":
                bash_path = shutil.which("bash")
                if bash_path:
                    result = subprocess.run([bash_path, str(script_to_run)], cwd=project.root)
                    return result.returncode
                else:
                    print_error("Bash is required to run .sh scripts on Windows. Please install Git Bash or WSL.")
                    return 1
            else:
                result = subprocess.run([str(script_to_run)], cwd=project.root)
                return result.returncode
        except Exception as e:
            print_error(f"Failed to start dev server: {e}")
            return 1

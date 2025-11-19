# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
import subprocess
import sys
import os
import shutil
from importlib import metadata as importlib_metadata
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
        self._check_uv()
        self._check_toml_support()
        self._check_environment()
        return 0

    def _check_docker(self):
        """Check Docker availability."""
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
            print_success("Docker is running")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print_warning("Docker not available or not running")

    def _check_python(self):
        """Check Python version."""
        # support sys.version_info tuples and objects with .major/.minor attributes
        maj = getattr(sys.version_info, "major", sys.version_info[0])
        minr = getattr(sys.version_info, "minor", sys.version_info[1])
        micro = getattr(sys.version_info, "micro", sys.version_info[2])
        version = f"{maj}.{minr}.{micro}"
        print_info(f"Python version: {version}")
        # Check supported Python range (restack-ai supports 3.10-3.12)
        if (maj, minr) < (3, 10) or (maj, minr) >= (3, 13):
            print_warning(
                "Python version outside supported range (recommended: 3.10-3.12). "
                "Some packages (like restack_ai) may not build on 3.13+ or work on <3.10"
            )

    def _check_packages(self):
        """Check required packages."""
        packages = ["jinja2", "restack_ai"]
        for pkg in packages:
            try:
                __import__(pkg)
                print_success(f"{pkg} installed")
            except ImportError:
                print_warning(f"{pkg} not installed")

        # Check restack_ai version and compatibility
        try:
            version = importlib_metadata.version("restack_ai")
            print_info(f"restack_ai version: {version}")
        except importlib_metadata.PackageNotFoundError:
            # Already warned above
            pass

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

    def _check_uv(self):
        """Check whether `uv` (venv helper) is available."""
        uv_path = shutil.which("uv")
        if uv_path:
            print_success(f"uv found at: {uv_path}")
        else:
            print_warning(
                "uv not found (recommended: install uv to create virtualenvs)."
            )

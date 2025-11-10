# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
import subprocess
import sys
import os
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
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print_info(f"Python version: {version}")

    def _check_packages(self):
        """Check required packages."""
        packages = ["jinja2", "restack_ai"]
        for pkg in packages:
            try:
                __import__(pkg)
                print_success(f"{pkg} installed")
            except ImportError:
                print_warning(f"{pkg} not installed")

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

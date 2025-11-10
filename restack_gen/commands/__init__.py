# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606

from typing import Optional, Dict, Type
from .base import Command
from ..constants import Config


class CommandRegistry:
    """Registry of all available commands."""

    def __init__(self, config: Config):
        self.config = config
        self._commands: Dict[str, Type[Command]] = {}
        self._register_commands()

    def _register_commands(self):
        """Register all available commands."""
        from .new import NewCommand
        from .generate import GenerateCommand
        from .routes import RoutesCommand
        from .dev import DevCommand
        from .build import BuildCommand
        from .test import RestackTestsCommand
        from .doctor import DoctorCommand
        from .info import VersionCommand, HelpCommand, ListTemplatesCommand

        self._commands = {
            "new": NewCommand,
            "g": GenerateCommand,
            "generate": GenerateCommand,
            "routes": RoutesCommand,
            "dev": DevCommand,
            "build": BuildCommand,
            "test": RestackTestsCommand,
            "doctor": DoctorCommand,
            "version": VersionCommand,
            "list-templates": ListTemplatesCommand,
            "ls-templates": ListTemplatesCommand,
            "help": HelpCommand,
        }

    def get(self, command: str) -> Optional[Command]:
        """Get command instance."""
        command_class = self._commands.get(command)
        if command_class:
            return command_class(self.config)
        return None

    def list_commands(self) -> list[str]:
        """List all unique command names."""
        seen = set()
        commands = []
        for name, cmd_class in self._commands.items():
            if cmd_class not in seen:
                commands.append(name)
                seen.add(cmd_class)
        return sorted(commands)

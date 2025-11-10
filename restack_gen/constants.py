# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VERSION = "0.2.0"


class Language(Enum):
    PYTHON = "py"
    TYPESCRIPT = "ts"


class GenerationType(Enum):
    AGENT = "agent"
    FUNCTION = "function"
    WORKFLOW = "workflow"


@dataclass
class Config:
    """Global configuration for the CLI."""

    lang: Optional[Language] = None
    package_manager: Optional[str] = None
    cwd: Optional[Path] = None
    quiet: bool = False
    yes: bool = False
    force: bool = False
    dry_run: bool = False
    verbose: bool = False
    no_color: bool = False

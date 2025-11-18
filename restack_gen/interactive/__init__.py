"""Interactive package for restack-gen.

This package is intentionally minimal; it provides a simple
InteractiveSession used by `cli_interactive`.
"""

from .session import InteractiveSession
from .prompts import InteractivePrompter

__all__ = ["InteractiveSession", "InteractivePrompter"]

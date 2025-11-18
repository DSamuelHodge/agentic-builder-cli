# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
"""restack-gen entrypoint dispatcher.

Decides whether to dispatch to the existing standard CLI or new
interactive mode based on argv and tty presence.
"""

from __future__ import annotations

import sys
from typing import Sequence


def should_use_interactive_mode(argv: Sequence[str] | None = None) -> bool:
    """Decide when to use interactive mode.

    Interactive mode is used when:
    - --interactive or -i provided
    - no args provided and attached to a TTY
    """
    if argv is None:
        argv = sys.argv[1:]

    # explicit flag
    if "--interactive" in argv or "-i" in argv:
        return True

    # no args and TTY
    if not argv and sys.stdin.isatty() and sys.stdout.isatty():
        return True

    # help or version should fall back to standard cli
    if any(arg in ["help", "--help", "-h", "--version", "-v"] for arg in argv):
        return False

    # common commands should use standard CLI
    standard_commands = ["new", "init", "build", "test", "deploy"]
    if argv and argv[0] in standard_commands:
        return False

    return False


def main(argv: Sequence[str] | None = None) -> int:
    """Main dispatcher entry point.

    Returns exit code from selected mode.
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        if should_use_interactive_mode(argv):
            from .cli_interactive import main as interactive_main

            return interactive_main(argv)
        else:
            from .cli import main as std_main

            return std_main(argv)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

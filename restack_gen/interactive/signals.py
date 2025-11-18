"""Signals handling for interactive mode."""

from __future__ import annotations

import signal
import sys
from typing import Callable


class SignalHandler:
    def __init__(self):
        self.interrupted = False
        self._original = {}

    def setup(self, cleanup: Callable | None = None) -> None:
        def _handle(signum, frame):
            self.interrupted = True
            if cleanup:
                try:
                    cleanup()
                except Exception:
                    pass
            sys.exit(130)

        self._original[signal.SIGINT] = signal.signal(signal.SIGINT, _handle)
        if hasattr(signal, "SIGTERM"):
            self._original[signal.SIGTERM] = signal.signal(signal.SIGTERM, _handle)

    def restore(self) -> None:
        for sig, handler in self._original.items():
            signal.signal(sig, handler)

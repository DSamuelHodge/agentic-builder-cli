"""Telemetry and usage analytics for restack-gen.

This module provides opt-in telemetry to help improve the tool.
All data collection is anonymous and respects user privacy.
"""

from __future__ import annotations

import json
import os
import platform
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class UsageMetrics:
    mode: str
    command: str
    success: bool
    duration_seconds: float
    error_type: str | None = None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "command": self.command,
            "success": self.success,
            "duration": self.duration_seconds,
            "error": self.error_type,
            "timestamp": datetime.utcnow().isoformat(),
        }


class MetricsCollector:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.config_dir = Path.home() / ".config" / "restack-gen"
        self.config_file = self.config_dir / "telemetry.json"
        self.session_start = time.time()

    def _load_config(self) -> Dict[str, Any]:
        """Load telemetry configuration."""
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_config(self, config: Dict[str, Any]):
        """Save telemetry configuration."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Silently fail if we can't save

    def enable(self):
        """Enable telemetry."""
        config = self._load_config()
        config["enabled"] = True
        self._save_config(config)
        self.enabled = True

    def disable(self):
        """Disable telemetry."""
        config = self._load_config()
        config["enabled"] = False
        self._save_config(config)
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if telemetry is enabled."""
        return self.enabled

    def record(self, metrics: UsageMetrics) -> None:
        if not self.enabled:
            return

        # Record to local log
        try:
            with open(".restack_metrics.log", "a", encoding="utf-8") as f:
                f.write(str(metrics.to_dict()) + "\n")
        except Exception:
            pass

        # Send anonymous telemetry event
        event_data = {
            "event": "command_used",
            "timestamp": time.time(),
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "session_duration": time.time() - self.session_start,
            "mode": metrics.mode,
            "command": metrics.command,
            "success": metrics.success,
            "duration": metrics.duration_seconds,
        }
        if metrics.error_type:
            event_data["error_type"] = metrics.error_type

        # In a real implementation, this would send to a telemetry service
        # For now, just debug logging
        if os.environ.get("RESTACK_TELEMETRY_DEBUG"):
            print(f"[TELEMETRY] {event_data}")

    def record_project_created(self, language: str, package_manager: str):
        """Record project creation."""
        if not self.enabled:
            return
        event_data = {
            "event": "project_created",
            "language": language,
            "package_manager": package_manager,
            "timestamp": time.time(),
        }
        if os.environ.get("RESTACK_TELEMETRY_DEBUG"):
            print(f"[TELEMETRY] {event_data}")

    def record_interactive_session(self, steps_completed: int, duration: float):
        """Record interactive session usage."""
        if not self.enabled:
            return
        event_data = {
            "event": "interactive_session",
            "steps_completed": steps_completed,
            "duration": duration,
            "timestamp": time.time(),
        }
        if os.environ.get("RESTACK_TELEMETRY_DEBUG"):
            print(f"[TELEMETRY] {event_data}")


# Global instance
_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
        # Load enabled state from config
        config = _collector._load_config()
        _collector.enabled = config.get("enabled", False)
    return _collector


def setup_telemetry_opt_in():
    """Prompt user to opt-in to telemetry on first run."""
    collector = get_collector()
    config = collector._load_config()

    if "opted_in" not in config:
        # For CLI, we don't prompt here; users can enable via command
        # This is just to set the flag
        config["opted_in"] = False
        collector._save_config(config)

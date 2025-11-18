"""Telemetry stub — optional, opt-in metrics collector."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


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

    def record(self, metrics: UsageMetrics) -> None:
        if not self.enabled:
            return
        # Minimal local logging to avoid privacy concerns
        try:
            with open(".restack_metrics.log", "a", encoding="utf-8") as f:
                f.write(str(metrics.to_dict()) + "\n")
        except Exception:
            pass

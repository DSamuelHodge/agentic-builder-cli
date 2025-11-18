"""Caching for interactive defaults and templates."""

from __future__ import annotations

from functools import lru_cache


class InteractiveCache:
    @staticmethod
    @lru_cache(maxsize=1)
    def get_templates():
        from .templates import TEMPLATES

        return TEMPLATES

    @staticmethod
    @lru_cache(maxsize=1)
    def get_user_context():
        from .context import UserContext

        return UserContext()

"""API layer for Binary Tree Visualizer."""
from __future__ import annotations

from typing import Any

__all__ = ["create_app", "app"]


def __getattr__(name: str) -> Any:
    """Lazy loader for Flask app and application factory."""
    if name in {"app", "create_app"}:
        from bt_visualizer.api.app import app as _app, create_app as _create_app

        if name == "app":
            return _app
        return _create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


"""Explicit opt-in overrides: route selected library calls to custom handlers.

Handler signature: handler(original_callable, *args, **kwargs).
Return what the caller expects, including an awaitable for asynchronous methods.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_handlers: dict[str, Callable[..., Any]] = {}


def register_override(name: str, handler: Callable[..., Any]) -> None:
    """Route calls named *name* through a handler instead of native forwarding."""
    if not isinstance(name, str) or not name:
        raise ValueError("Override name must be a nonempty string")
    if not callable(handler):
        raise TypeError("Override handler must be callable")
    _handlers[name] = handler


def unregister_override(name: str) -> None:
    """Restore native forwarding for a previously registered command."""
    _handlers.pop(name, None)


def get_override(name: str) -> Callable[..., Any] | None:
    return _handlers.get(name)

"""PyAutoGUI forwarding adapter. Requires the optional 'desktop' extra.

Designed to mirror ordinary PyAutoGUI attribute access while avoiding an OS / X11
backend import until it is first used. Each unchanged function logs on every call.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any

from inputweave._forward import forwarding_function

_backend = None


def _native():
    global _backend
    if _backend is None:
        try:
            _backend = importlib.import_module("pyautogui")
        except ImportError as exc:
            raise ImportError(
                "InputWeave's PyAutoGUI adapter requires pyautogui and an accessible desktop. "
                "Install it with: pip install 'inputweave[desktop]'"
            ) from exc
    return _backend


def __getattr__(name: str) -> Any:
    if name.startswith("_"):
        raise AttributeError(name)
    value = getattr(_native(), name)
    if inspect.isroutine(value) and not inspect.isclass(value):
        value = forwarding_function(value, f"pyautogui.{name}", wrap_result=False)
        globals()[name] = value  # Weave exactly once; log on each subsequent call.
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_native())))

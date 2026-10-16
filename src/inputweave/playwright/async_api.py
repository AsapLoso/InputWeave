"""Opt-in Playwright async API with wrapt-backed forwarding and per-call logs."""

import inspect
import playwright.async_api as _native
from inputweave._forward import AsyncManager, forwarding_function

for _name in dir(_native):
    if not _name.startswith("_"):
        _value = getattr(_native, _name)
        globals()[_name] = (forwarding_function(_value, _name)
                            if inspect.isfunction(_value) else _value)


def async_playwright():
    print("[InputWeave] Unchanged feature: async_playwright")
    return AsyncManager(_native.async_playwright())


__all__ = [name for name in dir(_native) if not name.startswith("_")]

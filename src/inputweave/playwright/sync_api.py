"""Opt-in Playwright sync API with wrapt-backed forwarding and per-call logs."""

import inspect
import playwright.sync_api as _native
from inputweave._forward import SyncManager, forwarding_function

for _name in dir(_native):
    if not _name.startswith("_"):
        _value = getattr(_native, _name)
        globals()[_name] = (forwarding_function(_value, _name)
                            if inspect.isfunction(_value) else _value)


def sync_playwright():
    print("[InputWeave] Unchanged feature: sync_playwright")
    return SyncManager(_native.sync_playwright())


__all__ = [name for name in dir(_native) if not name.startswith("_")]

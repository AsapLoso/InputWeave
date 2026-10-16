"""Opt-in Playwright sync API with unchanged-call logging."""

import functools
import inspect
import playwright.sync_api as _native
from inputweave._forward import SyncManager, forward_result, _unwrap


def _forward_function(value, label):
    @functools.wraps(value)
    def forwarded(*args, **kwargs):
        print(f"[InputWeave] Unchanged feature: {label}")
        return forward_result(value(*_unwrap(args), **_unwrap(kwargs)))
    return forwarded


for _name in dir(_native):
    if not _name.startswith("_"):
        _value = getattr(_native, _name)
        globals()[_name] = (_forward_function(_value, _name)
                            if inspect.isfunction(_value) else _value)


def sync_playwright():
    print("[InputWeave] Unchanged feature: sync_playwright")
    return SyncManager(_native.sync_playwright())


__all__ = [name for name in dir(_native) if not name.startswith("_")]

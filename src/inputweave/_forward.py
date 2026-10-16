"""Small forwarding proxy for Playwright objects (prototype, not full fidelity)."""

from __future__ import annotations

import functools
import inspect
from typing import Any


class ForwardProxy:
    """Forward attribute access and log each unchanged method invocation."""

    def __init__(self, target: Any):
        object.__setattr__(self, "_iw_target", target)

    @property
    def __wrapped__(self) -> Any:
        return self._iw_target

    def __getattr__(self, name: str) -> Any:
        target = object.__getattribute__(self, "_iw_target")
        value = getattr(target, name)  # Preserve AttributeError for missing names.
        if not callable(value):
            return forward_result(value)
        if inspect.isclass(value):
            return value
        label = f"{type(target).__name__}.{name}"
        if inspect.iscoroutinefunction(value):
            @functools.wraps(value)
            async def async_forward(*args: Any, **kwargs: Any) -> Any:
                print(f"[InputWeave] Unchanged feature: {label}")
                result = await value(*_unwrap(args), **_unwrap(kwargs))
                return forward_result(result)
            return async_forward

        @functools.wraps(value)
        def forward(*args: Any, **kwargs: Any) -> Any:
            print(f"[InputWeave] Unchanged feature: {label}")
            result = value(*_unwrap(args), **_unwrap(kwargs))
            return forward_result(result)
        return forward

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._iw_target, name, _unwrap(value))

    def __repr__(self) -> str:
        return f"ForwardProxy({self._iw_target!r})"


def _unwrap(value: Any) -> Any:
    if isinstance(value, ForwardProxy):
        return value.__wrapped__
    if isinstance(value, list):
        return [_unwrap(x) for x in value]
    if isinstance(value, tuple):
        return tuple(_unwrap(x) for x in value)
    if isinstance(value, dict):
        return {k: _unwrap(v) for k, v in value.items()}
    return value


def forward_result(value: Any) -> Any:
    """Only proxy Playwright API objects; preserve ordinary Python values."""
    if isinstance(value, ForwardProxy):
        return value
    if isinstance(value, list):
        return [forward_result(x) for x in value]
    if isinstance(value, tuple):
        return tuple(forward_result(x) for x in value)
    module = type(value).__module__
    if module.startswith(("playwright.sync_api", "playwright.async_api")):
        return ForwardProxy(value)
    return value


class SyncManager:
    def __init__(self, manager: Any):
        self._manager = manager

    def __enter__(self) -> Any:
        print("[InputWeave] Unchanged feature: PlaywrightContextManager.__enter__")
        return forward_result(self._manager.__enter__())

    def start(self) -> Any:
        print("[InputWeave] Unchanged feature: PlaywrightContextManager.start")
        return forward_result(self._manager.start())

    def __exit__(self, *args: Any) -> Any:
        print("[InputWeave] Unchanged feature: PlaywrightContextManager.__exit__")
        return self._manager.__exit__(*args)


class AsyncManager:
    def __init__(self, manager: Any):
        self._manager = manager

    async def __aenter__(self) -> Any:
        print("[InputWeave] Unchanged feature: PlaywrightContextManager.__aenter__")
        return forward_result(await self._manager.__aenter__())

    async def start(self) -> Any:
        print("[InputWeave] Unchanged feature: PlaywrightContextManager.start")
        return forward_result(await self._manager.start())

    async def __aexit__(self, *args: Any) -> Any:
        print("[InputWeave] Unchanged feature: PlaywrightContextManager.__aexit__")
        return await self._manager.__aexit__(*args)

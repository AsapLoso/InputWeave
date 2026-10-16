"""Forward Playwright objects through wrapt rather than rewriting their proxy semantics."""

from __future__ import annotations

import inspect
from typing import Any

import wrapt


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


def forwarding_function(original: Any, label: str, *, wrap_result: bool = True) -> Any:
    """Create a bound-method-aware wrapper once; print on *each invocation*."""

    if inspect.iscoroutinefunction(original):
        async def call(wrapped: Any, instance: Any, args: tuple, kwargs: dict) -> Any:
            print(f"[InputWeave] Unchanged feature: {label}")
            result = await wrapped(*_unwrap(args), **_unwrap(kwargs))
            return forward_result(result) if wrap_result else result
    else:
        def call(wrapped: Any, instance: Any, args: tuple, kwargs: dict) -> Any:
            print(f"[InputWeave] Unchanged feature: {label}")
            result = wrapped(*_unwrap(args), **_unwrap(kwargs))
            return forward_result(result) if wrap_result else result

    return wrapt.FunctionWrapper(original, call)


class ForwardProxy(wrapt.ObjectProxy):
    """A wrapt-backed adapter: nested API objects and methods remain proxied."""

    def __getattribute__(self, name: str) -> Any:
        result = super().__getattribute__(name)
        if name in {"__wrapped__", "__class__", "__dict__", "__weakref__"} or name.startswith("_self_"):
            return result
        if inspect.isclass(result):
            return result
        if callable(result):
            label = f"{type(self.__wrapped__).__name__}.{name}"
            return forwarding_function(result, label)
        return forward_result(result)


def forward_result(value: Any) -> Any:
    """Recursively wrap Playwright API objects but leave Python values intact."""
    if isinstance(value, ForwardProxy):
        return value
    if isinstance(value, list):
        return [forward_result(x) for x in value]
    if isinstance(value, tuple):
        return tuple(forward_result(x) for x in value)
    if isinstance(value, dict):
        return {k: forward_result(v) for k, v in value.items()}
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

"""Forwarding tests without external display or browser installation."""

import asyncio
import inspect
import sys
import types

import pytest

from inputweave._forward import ForwardProxy, forward_result, forwarding_function


class NestedMouse:
    __module__ = "playwright.sync_api._generated"

    def click(self, x, y):
        return (x, y)


class NestedPage:
    __module__ = "playwright.sync_api._generated"

    def __init__(self):
        self.mouse = NestedMouse()

    def title(self):
        return "Ready"

    def values(self):
        return [NestedMouse()]


class AsyncMouse:
    __module__ = "playwright.async_api._generated"

    async def click(self, x, y):
        return (x, y)


def test_nested_method_forwarding(capsys):
    raw = NestedPage()
    page = forward_result(raw)
    assert isinstance(page, NestedPage)
    assert page.mouse.click(12, 34) == (12, 34)
    assert page.title() == "Ready"
    assert page.values()[0].click(2, 3) == (2, 3)
    assert raw.mouse is page.mouse.__wrapped__
    out = capsys.readouterr().out
    assert out.count("Unchanged feature: NestedMouse.click") == 2
    assert "Unchanged feature: NestedPage.title" in out
    assert "Unchanged feature: NestedPage.values" in out


def test_async_nested_method_forwarding(capsys):
    mouse = forward_result(AsyncMouse())
    assert inspect.iscoroutinefunction(mouse.click)
    assert asyncio.run(mouse.click(2, 4)) == (2, 4)
    assert "Unchanged feature: AsyncMouse.click" in capsys.readouterr().out


def test_pyautogui_lazy_import_and_print(monkeypatch, capsys):
    import inputweave.pyautogui as bridge
    monkeypatch.setattr(bridge, "_backend", None)
    bridge.__dict__.pop("click", None)
    fake = types.ModuleType("pyautogui")
    calls = []

    def click(x, y):
        calls.append((x, y))
        return "clicked"

    fake.click = click
    fake.PAUSE = 0.1
    monkeypatch.setitem(sys.modules, "pyautogui", fake)
    try:
        assert bridge.PAUSE == 0.1
        assert bridge.click(2, 3) == "clicked"
        assert bridge.click(4, 5) == "clicked"
        assert calls == [(2, 3), (4, 5)]
        assert capsys.readouterr().out.count("Unchanged feature: pyautogui.click") == 2
    finally:
        bridge.__dict__.pop("click", None)
        bridge._backend = None


def test_forward_preserves_exception(capsys):
    def native():
        raise RuntimeError("backend error")

    wrapped = forwarding_function(native, "native")
    with pytest.raises(RuntimeError, match="backend error"):
        wrapped()
    assert "Unchanged feature: native" in capsys.readouterr().out

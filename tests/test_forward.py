import asyncio
import inspect

import pytest

from inputweave._forward import ForwardProxy, forward_result
from inputweave.playwright.sync_api import sync_playwright
from inputweave.playwright.async_api import async_playwright


class Fake:
    def __init__(self):
        self.value = 7

    def add(self, value):
        return self.value + value

    def fail(self):
        raise ValueError("native error")

    async def aadd(self, value):
        return self.value + value


def test_native_passthrough(capsys):
    proxy = ForwardProxy(Fake())
    assert proxy.value == 7
    assert proxy.add(5) == 12
    assert proxy.add(1) == 8
    assert capsys.readouterr().out.count("Unchanged feature: Fake.add") == 2
    with pytest.raises(ValueError, match="native error"):
        proxy.fail()


def test_async_method(capsys):
    proxy = ForwardProxy(Fake())
    assert inspect.iscoroutinefunction(proxy.aadd)
    assert asyncio.run(proxy.aadd(3)) == 10
    assert "Unchanged feature: Fake.aadd" in capsys.readouterr().out


def test_playwright_sync_without_browser(capsys):
    with sync_playwright() as p:
        assert p.chromium.name == "chromium"
        # Methods are forwarded through nested objects; no browser installation needed.
        assert p.chromium.executable_path
    out = capsys.readouterr().out
    assert "Unchanged feature: sync_playwright" in out
    assert "Unchanged feature: PlaywrightContextManager.__enter__" in out


def test_playwright_async_without_browser(capsys):
    async def run():
        async with async_playwright() as p:
            assert p.chromium.name == "chromium"
            assert p.chromium.executable_path
    asyncio.run(run())
    assert "Unchanged feature: async_playwright" in capsys.readouterr().out


def test_missing_attribute_preserves_error():
    with pytest.raises(AttributeError):
        ForwardProxy(Fake()).missing_feature


def test_sync_start_stop(capsys):
    p = sync_playwright().start()
    try:
        assert p.firefox.name == "firefox"
        assert callable(p.stop)
    finally:
        p.stop()
    out = capsys.readouterr().out
    assert "Unchanged feature: PlaywrightContextManager.start" in out
    assert "Unchanged feature: Playwright.stop" in out


def test_async_start_stop(capsys):
    async def run():
        p = await async_playwright().start()
        try:
            assert p.webkit.name == "webkit"
        finally:
            await p.stop()
    asyncio.run(run())
    assert "Unchanged feature: PlaywrightContextManager.start" in capsys.readouterr().out

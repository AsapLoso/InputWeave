"""Optional real-browser tests: INPUTWEAVE_BROWSER_SMOKE=1 pytest tests/test_browser_smoke.py"""

import asyncio
import os
import shutil

import pytest

if os.environ.get("INPUTWEAVE_BROWSER_SMOKE") != "1":
    pytest.skip("Set INPUTWEAVE_BROWSER_SMOKE=1 to run Chromium smoke tests", allow_module_level=True)

chromium = shutil.which("chromium") or shutil.which("chromium-browser")
if not chromium:
    pytest.skip("Chromium executable not found", allow_module_level=True)


def test_sync_locator_click():
    from inputweave.playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=chromium)
        try:
            page = browser.new_page()
            page.set_content('<button id="go" onclick="document.title=\'clicked\'">Go</button>')
            page.locator("#go").click()
            assert page.title() == "clicked"
        finally:
            browser.close()


def test_async_mouse_click():
    from inputweave.playwright.async_api import async_playwright

    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, executable_path=chromium)
            try:
                page = await browser.new_page()
                await page.set_content('<button id="go" onclick="document.title=\'clicked\'">Go</button>')
                await page.mouse.click(15, 15)
                assert await page.title() == "clicked"
            finally:
                await browser.close()

    asyncio.run(run())

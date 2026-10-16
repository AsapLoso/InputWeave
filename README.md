# InputWeave

**Experimental opt-in forwarding middleware for selected Python browser and desktop automation libraries.**

Use a familiar library interface through an InputWeave import path. Unchanged function calls print their name and delegate to the real library. Future adapters can selectively override individual methods.

> **Status (2026-10-16): forwarding-only prototype, not production-ready.** There are no custom interaction overrides or anti-detection features.

## Scope

| Library | Current support | Original backend |
| --- | --- | --- |
| [Playwright Python](https://playwright.dev/python/) | **Prototype:** synchronous and asynchronous entry points, nested browser/page/mouse/locator methods | Playwright |
| [PyAutoGUI](https://pyautogui.readthedocs.io/) | **Prototype:** lazy-loading module functions and constants | PyAutoGUI |
| [pynput](https://pynput.readthedocs.io/) | **Not implemented:** planned for evaluation | — |

Only scripts **explicitly importing from InputWeave** are affected. Ordinary imports from the original packages remain unchanged. No arbitrary Python modules or desktop applications are modified.

## Installation

```sh
git clone https://github.com/AsapLoso/InputWeave.git
cd InputWeave
python -m pip install -e ".[test]"
python -m pytest -q
```

For PyAutoGUI, also install its optional backend dependency:

```sh
python -m pip install -e ".[desktop,test]"
```

PyAutoGUI requires a working graphical desktop; importing the InputWeave adapter itself does **not** require a display until you access a PyAutoGUI attribute.

## Playwright example

Change one import:

```python
# Native:
# from playwright.sync_api import sync_playwright

# InputWeave:
from inputweave.playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```

The async counterpart is `from inputweave.playwright.async_api import async_playwright`.

Sample output:

```text
[InputWeave] Unchanged feature: sync_playwright
[InputWeave] Unchanged feature: PlaywrightContextManager.__enter__
[InputWeave] Unchanged feature: BrowserType.launch
[InputWeave] Unchanged feature: Browser.new_page
[InputWeave] Unchanged feature: Page.goto
[InputWeave] Unchanged feature: Page.title
[InputWeave] Unchanged feature: Browser.close
[InputWeave] Unchanged feature: PlaywrightContextManager.__exit__
```

## PyAutoGUI example

```python
# Native:
# import pyautogui

# InputWeave:
import inputweave.pyautogui as pyautogui

pyautogui.click(400, 250)
pyautogui.write("Hello")
```

Every unchanged function call prints a message and then calls the real PyAutoGUI function. The adapter imports PyAutoGUI on first attribute access and caches function wrappers after the first lookup.

**Current limitation:** reading attributes and calling functions are supported, but writing PyAutoGUI's mutable module settings such as `PAUSE` via the InputWeave module is **not** transparently forwarded. Nor is the module guaranteed to support every unusual import or type-introspection pattern.

## Implementation

InputWeave reuses [wrapt](https://github.com/GrahamDumpleton/wrapt) for Playwright object proxies and function wrappers rather than rebuilding object descriptor behavior in Python. Playwright context-manager entry/exit requires a small adapter.

Per-call passthrough messages are **intentional and on by default**. The wrappers add Python overhead and printing can be especially costly for very cheap methods. This has not been benchmarked.

## Verification

- 11 unit/smoke tests pass locally, including Playwright sync/async startup, nested method forwarding, exception behavior, and PyAutoGUI delegation with a fake backend.
- Two optional real Chromium tests passed locally: sync locator click and async mouse click.
- Run the optional browser checks with a system Chromium executable:

```sh
INPUTWEAVE_BROWSER_SMOKE=1 python -m pytest tests/test_browser_smoke.py
```

Playwright compatibility remains incomplete, particularly special methods, events, callbacks, object identity, and nontrivial context managers. The current browser tests are only a narrow smoke check.

## Roadmap

1. Expand Playwright compatibility tests (events, callbacks, locator context managers, browser exceptions).
2. Evaluate a more complete PyAutoGUI module proxy for mutable module settings.
3. Add a selective override registry **after** passthrough semantics are reliable.
4. Evaluate a pynput adapter without breaking controller class semantics.

See [STATE.md](STATE.md) for project state and the explicitly low-priority GitHub-description TODO.

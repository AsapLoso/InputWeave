# InputWeave

**Experimental opt-in forwarding middleware for selected Python browser and desktop automation libraries.**

Use a familiar library interface through an InputWeave import path. Unchanged function calls print their name and delegate to the real library. Registered handlers can selectively route methods elsewhere; unregistered calls use the original backend.

> **Status (2026-10-16): forwarding and optional motion-preset prototype, not production-ready.** An override registry and a PyTweening-backed PyAutoGUI movement preset are available. No custom trajectory generator or anti-detection features are bundled.

## Scope

| Library | Current support | Original backend |
| --- | --- | --- |
| [Playwright Python](https://playwright.dev/python/) | **Prototype:** synchronous and asynchronous entry points, nested browser/page/mouse/locator methods | Playwright |
| [PyAutoGUI](https://pyautogui.readthedocs.io/) | **Prototype:** lazy-loading module functions and constants; optional eased movement/dragging | PyAutoGUI |
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

## Optional motion integration (PyAutoGUI + PyTweening)

The first movement layer **reuses existing libraries**, rather than writing a trajectory engine: [PyTweening](https://github.com/asweigart/pytweening) provides easing functions, and **native PyAutoGUI** performs the actual movement or drag.

```sh
python -m pip install -e ".[desktop,motion,test]"
```

```python
import inputweave.pyautogui as pyautogui
from inputweave.motion import eased_pyautogui_moves

# Opt-in defaults; ordinary calls remain native.
with eased_pyautogui_moves(duration=0.3, curve="easeInOutSine"):
    pyautogui.moveTo(400, 250)
    pyautogui.moveRel(20, 10)
    pyautogui.dragTo(450, 300)

# Outside the context, native forwarding with per-call print resumes.
pyautogui.moveTo(500, 300)
```

Within the context, InputWeave routes `moveTo`, `moveRel`, `dragTo`, and `dragRel` through a registered override that supplies `duration` and `tween`. **Explicit parameters win** over those defaults. On exit, previous handlers are restored, including if an exception occurs. There are no global PyAutoGUI setting changes.

The feature has been unit-tested with a stub PyAutoGUI backend, **not against a real graphical desktop**. It produces eased *straight-line* movement, not Bézier curves or Perlin noise. The initial scope is deliberately limited and does **not** alter Playwright mouse calls.

**Dependency choice:** [PyClick](https://github.com/patrikoss/pyclick) offers curved mouse trajectories, but its import initializes PyAutoGUI and changes its global timing variables, making it a poor fit for an unobtrusive default. It could be revisited behind strict isolation later.

**Concurrency warning:** InputWeave's override registry is process-global; simultaneous or overlapping motion contexts across threads are currently unsupported.

## Route a method through another implementation

An explicit override registry can route an intercepted command to your own implementation or an existing library. Nothing is changed by default.

```python
from inputweave import register_override, unregister_override
from inputweave.playwright.sync_api import sync_playwright

def custom_click(original_click, x, y, **kwargs):
    # Delegate to the native backend, or call another permitted input backend.
    return original_click(x, y, **kwargs)

register_override("Mouse.click", custom_click)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.mouse.click(100, 100)  # custom_click receives this call
        browser.close()
finally:
    unregister_override("Mouse.click")
```

Handlers receive the original callable first, followed by its arguments. Asynchronous overrides can be `async def` functions. Other methods continue printing `Unchanged feature: ...` on every call. Handler registration is process-global at present, and class-specific keys such as `Mouse.click` apply to all proxied objects of that class. **There is no per-context isolation or thread-safety guarantee yet.**

## Implementation

InputWeave reuses [wrapt](https://github.com/GrahamDumpleton/wrapt) for Playwright object proxies and function wrappers rather than rebuilding object descriptor behavior in Python. Playwright context-manager entry/exit requires a small adapter.

Per-call passthrough messages are **intentional and on by default**. The wrappers add Python overhead and printing can be especially costly for very cheap methods. This has not been benchmarked.

## Verification

- GitHub Actions: **22 passed, 1 optional browser test module skipped** on Python 3.10, 3.11, and 3.12. Coverage includes the PyTweening motion preset with a fake PyAutoGUI backend, Playwright sync/async startup, and override restoration.
- Two optional real Chromium tests passed locally: sync locator click and async mouse click.
- Run the optional browser checks with a system Chromium executable:

```sh
INPUTWEAVE_BROWSER_SMOKE=1 python -m pytest tests/test_browser_smoke.py
```

Playwright compatibility remains incomplete, particularly special methods, events, callbacks, object identity, and nontrivial context managers. The current browser tests are only a narrow smoke check.

## Roadmap

1. Expand Playwright compatibility tests (events, callbacks, locator context managers, browser exceptions).
2. Evaluate a more complete PyAutoGUI module proxy for mutable module settings.
3. Improve the initial override registry: configuration, context-scoped isolation, and API compatibility tests.
4. Add an optional *curved-path* backend only if a library can be integrated without global desktop side effects; evaluate a pynput adapter separately.

See [STATE.md](STATE.md) for project state and the explicitly low-priority GitHub-description TODO.

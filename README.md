# InputWeave

**Selective, drop-in interception for supported Python GUI and browser automation libraries.**

InputWeave aims to let a script keep using a familiar automation-library API while routing selected calls through a middleware layer. Methods without an override are forwarded to the original library and print a short passthrough message.

> **Status: concept / initial design.** This repository does not yet contain a working Python package or a verified drop-in adapter.

## Scope: opt-in and library-specific

InputWeave is **not** a system-wide input hook, a replacement for every Python import, or a general-purpose wrapper around arbitrary software. It only affects code that explicitly imports an InputWeave adapter for a **supported library**.

| Library | Scope | Status |
| --- | --- | --- |
| [Playwright for Python](https://playwright.dev/python/) | Browser automation; first target, including nested page/mouse/locator APIs and sync/async compatibility | **Planned; not implemented** |
| [PyAutoGUI](https://pyautogui.readthedocs.io/) | Desktop mouse and keyboard controls | **Possible later adapter; not implemented** |
| [pynput](https://pynput.readthedocs.io/) | Desktop input controllers | **Possible later adapter; not implemented** |

Other libraries remain **out of scope unless an adapter is added**. Installing InputWeave alone should not modify the behavior of ordinary Playwright, PyAutoGUI, or pynput imports.

## Intended usage

The goal is to **change the import, not the calls**.

```python
# Native Playwright
from playwright.sync_api import sync_playwright

# Proposed InputWeave replacement (illustrative; NOT implemented yet)
from inputweave.playwright.sync_api import sync_playwright
```

The rest of a Playwright script would ideally remain unchanged:

```python
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    page.mouse.click(400, 250)
    print(page.title())
    browser.close()
```

## Behavior contract (proposed)

1. **Override:** When InputWeave has an override for a supported method, invoke it while preserving the original API's expected behavior.
2. **Forward:** Otherwise, print a message such as `[InputWeave] Unchanged feature: Page.title` **on every call**, then delegate directly to the original method with the same arguments.
3. **Preserve compatibility:** Retain return values, exceptions, method binding, sync/async behavior, and nested objects. Do not silently change semantics.
4. **Opt in:** Native library imports continue to behave normally; only InputWeave-prefixed imports take this path.

The wrappers can be created once during adapter initialization, avoiding repeated discovery or patch setup. Each forwarded call still incurs some Python wrapper overhead, and console printing may dominate the overhead of very fast native calls. No performance claims have been benchmarked yet.

## First milestone

Implement **forwarding-only** support for one library (Playwright for Python). Verify import-prefix substitution, nested objects, synchronous and asynchronous calls, error propagation, and the per-call passthrough print. **Do not add custom mouse trajectories or behavioral changes until transparent forwarding passes tests.**

Potential implementation building blocks include [wrapt](https://github.com/GrahamDumpleton/wrapt) for transparent wrappers and [aspectlib](https://github.com/ionelmc/python-aspectlib) for weaving. These are candidates, not dependencies currently installed by this repository.

## Non-goals

- Automatically altering all Python libraries or existing scripts.
- Promising compatibility with libraries for which no adapter exists.
- Concealing automated access or bypassing websites' anti-bot restrictions.

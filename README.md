# InputWeave

**Experimental, opt-in middleware for selected Python browser and desktop automation libraries.**

InputWeave aims to keep a library's familiar interface while routing selected calls through middleware. Calls without an override print a passthrough message and then use the original library.

> **Status (2026-10-16): early forwarding-only prototype.** Only a Playwright Python adapter exists so far; compatibility is partial and browser interaction is not yet validated. There are no custom interaction overrides.

## Supported scope

| Library | Status |
| --- | --- |
| [Playwright for Python](https://playwright.dev/python/) | **Initial forwarding-only prototype:** sync and async entry points; basic nested object forwarding |
| [PyAutoGUI](https://pyautogui.readthedocs.io/) | **Not implemented; possible later adapter** |
| [pynput](https://pynput.readthedocs.io/) | **Not implemented; possible later adapter** |

InputWeave **does not affect ordinary library imports**. Only scripts explicitly importing an `inputweave` adapter use it; unsupported libraries are unaffected.

## Try the Playwright prototype

Requires Python 3.10+:

```sh
git clone https://github.com/AsapLoso/InputWeave.git
cd InputWeave
python -m pip install -e ".[test]"
python -m pytest -q
```

Change only the import in a conventional Playwright script:

```python
# Before:
# from playwright.sync_api import sync_playwright

# After:
from inputweave.playwright.sync_api import sync_playwright

with sync_playwright() as p:
    print(p.chromium.name)
    # Existing Playwright calls should forward through the adapter.
```

For async code, use `from inputweave.playwright.async_api import async_playwright`.

Example console output:

```text
[InputWeave] Unchanged feature: sync_playwright
[InputWeave] Unchanged feature: PlaywrightContextManager.__enter__
[InputWeave] Unchanged feature: PlaywrightContextManager.__exit__
```

The test suite uses real Playwright startup without launching a browser. Installing Playwright browsers is not necessary to run these smoke tests, but will be necessary for future end-to-end browser tests.

## Current forwarding behavior

- Native Playwright sync and async context managers are available, including `.start()`.
- Ordinary callable attributes on proxied Playwright objects print **on every call** and delegate to the original method.
- Returned Playwright API objects are recursively proxied, including within lists and tuples.
- Python values and attributes that are not callable generally pass through unchanged.
- Underlying native exceptions propagate.

**Known limitations:** A lightweight Python proxy is not perfectly type-transparent. It does not yet preserve every special method, event context manager, callback interaction, object identity, or Playwright class compatibility guarantee. There are no tests for live browser/page/locator interactions yet. Console output and Python wrappers add overhead; no performance benchmarking has been done. Do not assume full drop-in compatibility until these gaps are addressed.

## Next milestones

1. Add tests against real browser/page/mouse/locator workflows, both sync and async.
2. Evaluate whether `wrapt` improves type transparency and special-method forwarding; reuse existing tooling where it actually solves the compatibility gaps.
3. Introduce a selective override registry **after** forwarding is proven.
4. Consider additional library adapters only after the first is stable.

No stealth or anti-bot evasion functionality is planned.

See [STATE.md](STATE.md) for project status and the low-priority GitHub-description TODO.

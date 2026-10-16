# InputWeave — Project State

Updated: 2026-10-16

## Current implementation (experimental)

- Public standalone Python repository; version label `0.0.2` in source (not published to PyPI).
- **Playwright Python**: sync/async import-prefix adapters; nested browser/page/mouse/locator passthrough; special start/context-manager entry points.
- **PyAutoGUI**: opt-in, lazy module-function passthrough via `inputweave.pyautogui`; original PyAutoGUI remains the backend; requires actual desktop on use.
- **wrapt**: established library now supplies function wrappers and object proxies, avoiding bespoke descriptors and special-method proxy code.
- **Per-call logging**: unchanged functions print `[InputWeave] Unchanged feature: …` on every invocation.
- **Local verification**: 11 unit tests pass; two optional real Chromium tests pass (sync locator click and async mouse click).
- **No custom overrides yet. No bot-evasion features. No full API compatibility guarantee.**

## Known limitations

- Playwright proxy methods are created on attribute access; wrappers are not globally installed once for every nested method.
- Event context managers, callbacks, instance identity, special methods, and full browser behavior need further testing.
- PyAutoGUI module-level mutable settings (e.g. `PAUSE`) are not forwarded on assignment; desktop interaction hasn't been tested here on a real OS desktop.
- pynput adapter is **not implemented**; controller type identity needs deliberate design.
- wrapt does not eliminate Python logging cost.

## Next steps

1. Broaden sync/async Playwright browser integration coverage; pay special attention to callback, event, special-method semantics.
2. Choose a safe mutable-setting strategy for PyAutoGUI; test actual desktop backend when available.
3. Implement explicit selective override registration once forwarding is stable.
4. Evaluate pynput as a separate adapter rather than implying unsupported functionality exists.

## Very low priority — quick maintenance (approx. 2 minutes)

- [ ] **P4 / cosmetic:** Update GitHub repository short **About** description only when convenient; leave it unchanged for now. Proposed: `Opt-in forwarding middleware for Playwright Python and PyAutoGUI; selective overrides planned.`
- Not an engineering blocker. Do not displace the tests or adapter work.

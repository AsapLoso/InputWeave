# InputWeave — Project State

Updated: 2026-10-16

## Current implementation (experimental)

- Public standalone Python repository; version label `0.0.2` in source (not published to PyPI).
- **Playwright Python**: sync/async import-prefix adapters; nested browser/page/mouse/locator passthrough; special start/context-manager entry points.
- **PyAutoGUI**: opt-in, lazy module-function passthrough via `inputweave.pyautogui`; original PyAutoGUI remains the backend; requires actual desktop on use.
- **wrapt**: established library now supplies function wrappers and object proxies, avoiding bespoke descriptors and special-method proxy code.
- **Per-call logging**: unchanged functions print `[InputWeave] Unchanged feature: …` on every invocation.
- **Local verification**: 14 unit tests pass; two optional real Chromium tests pass (sync locator click and async mouse click).
- **Explicit routing registry**: register/unregister handlers by method label (e.g. \`Mouse.click\` or \`pyautogui.click\`); unregistered calls forward with per-call logs. No bundled custom motion implementation, no bot-evasion features, no full API compatibility guarantee.

## Known limitations

- Playwright proxy methods are created on attribute access; wrappers are not globally installed once for every nested method.
- Event context managers, callbacks, instance identity, special methods, and full browser behavior need further testing.
- PyAutoGUI module-level mutable settings (e.g. `PAUSE`) are not forwarded on assignment; desktop interaction hasn't been tested here on a real OS desktop.
- pynput adapter is **not implemented**; controller type identity needs deliberate design.
- Overrides are currently global to the interpreter and not isolated by session or thread; no concurrency guarantees.\n- wrapt does not eliminate Python logging cost.

## Next steps

1. Broaden sync/async Playwright browser integration coverage; pay special attention to callback, event, special-method semantics.
2. Choose a safe mutable-setting strategy for PyAutoGUI; test actual desktop backend when available.
3. Harden the basic override registry (context-scoping / concurrency and error semantics) before third-party motion backends.
4. Evaluate pynput as a separate adapter rather than implying unsupported functionality exists.

## Very low priority — quick maintenance (approx. 2 minutes)

- [ ] **P4 / cosmetic:** Update GitHub repository short **About** description only when convenient; leave it unchanged for now. Proposed: `Opt-in forwarding middleware for Playwright Python and PyAutoGUI; selective overrides planned.`
- Not an engineering blocker. Do not displace the tests or adapter work.

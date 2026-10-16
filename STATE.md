# InputWeave — Project State

Updated: 2026-10-16

## InputWeave goal — keep it in sight

**Goal:** a small, reusable, opt-in, import-prefix-compatible middleware for a **known and limited list of Python GUI/browser automation libraries**. Do not rebuild existing motion/input libraries. Forward every unchanged method through its native backend while printing one passthrough message **per call**; let registered overrides delegate selected calls to established third-party libraries. Preserve native semantics, async behavior and failure modes wherever feasible.

**Working habit:** Keep an eye on this goal. At the start of a development session and periodically during substantial changes, reread it and check whether changes reduce duplicated code, maintain import compatibility, and keep unsupported libraries explicitly out of scope. Update this state after verified milestones. This is an ongoing engineering habit, **not a scheduled background task or a project named ICE**.

## Current implementation (experimental)

- Public standalone Python repository; version label `0.0.3` in source (not published to PyPI).
- **Playwright Python**: sync/async import-prefix adapters; nested browser/page/mouse/locator passthrough; special start/context-manager entry points.
- **PyAutoGUI**: opt-in, lazy module-function passthrough via `inputweave.pyautogui`; original PyAutoGUI remains the backend; requires actual desktop on use.
- **PyTweening**: optional integration for eased PyAutoGUI move/drag calls, via native PyAutoGUI duration/tween parameters; defaults only inside an explicit context; preserves pre-existing overrides.
- **wrapt**: established library now supplies function wrappers and object proxies, avoiding bespoke descriptors and special-method proxy code.
- **Per-call logging**: unchanged functions print `[InputWeave] Unchanged feature: …` on every invocation.
- **Verification**: GitHub Actions reports **22 passed, 1 skipped** on Python 3.10, 3.11, and 3.12. The skipped module contains optional real-Chromium tests. Prior local checks recorded two real Chromium smoke passes; the new motion preset is tested against a fake PyAutoGUI backend only.
- **Explicit routing registry**: register/unregister handlers by method label (e.g. `Mouse.click` or `pyautogui.click`); unregistered calls forward with per-call logs. PyTweening movement easing preset with native PyAutoGUI execution (opt-in; no curved-path generator), no bot-evasion features, no full API compatibility guarantee.

## Known limitations

- Playwright proxy methods are created on attribute access; wrappers are not globally installed once for every nested method.
- Event context managers, callbacks, instance identity, special methods, and full browser behavior need further testing.
- Motion preset is tested with a fake desktop backend only; no physical mouse verification yet.
- PyAutoGUI module-level mutable settings (e.g. `PAUSE`) are not forwarded on assignment; desktop interaction hasn't been tested here on a real OS desktop.
- pynput adapter is **not implemented**; controller type identity needs deliberate design.
- Overrides are currently global to the interpreter and not isolated by session or thread; no concurrency guarantees.
- wrapt does not eliminate Python logging cost.

## Next steps

1. Broaden sync/async Playwright browser integration coverage; pay special attention to callback, event, special-method semantics.
2. Choose a safe mutable-setting strategy for PyAutoGUI; test actual desktop backend when available.
3. Harden the basic override registry (context-scoping / concurrency and error semantics); current motion preset is process-global.
4. Investigate optional curved-path generators without import-time global side effects; keep pynput as a separate evaluation.

## CI hygiene — 2026-10-16

- **Cause of notification noise:** 29 push-triggered workflow runs during early implementation, with 6 historical failures. Four failed before `wrapt` was declared; two failed before the motion dependency `pytweening` was installed in CI. Both dependencies are now configured and the subsequent runs passed.
- **Fix:** `.github/workflows/tests.yml` now ignores README/state-only pushes, limits branch push builds to `main`, and cancels superseded runs on the same ref. Keep the three Python-version checks.
- **Working rule:** stage a coherent vertical slice and commit/push its files **atomically**; do not commit one file at a time while the repository is in a temporarily inconsistent state. Run tests before pushing when practical.
- Historical GitHub Actions failures remain visible; their emails may already have been sent. Don't disable all CI or failure notifications to conceal genuine future failures.

## Very low priority — quick maintenance (approx. 2 minutes)

- [ ] **P4 / cosmetic:** Update GitHub repository short **About** description only when convenient; leave it unchanged for now. Proposed: `Opt-in forwarding middleware for Playwright Python and PyAutoGUI; selective overrides planned.`
- Not an engineering blocker. Do not displace the tests or adapter work.

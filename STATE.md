# InputWeave — Project State

Updated: 2026-10-16

## Current implementation

- Standalone public Python package prototype in `src/inputweave/`.
- **Playwright Python only:** forwarding wrappers for `sync_playwright` and `async_playwright`, native context-manager and `.start()` usage, basic nested-object method forwarding.
- **Default behavior:** print `[InputWeave] Unchanged feature: <API.method>` on every unchanged method invocation, then forward to the native implementation.
- **Not implemented:** configurable overrides, custom trajectories, PyAutoGUI/pynput adapters, and proven compatibility for full browser workflows.
- **Verified locally:** 7 pytest tests passed using real Playwright startup without browser launch. These are smoke/unit tests, not production compatibility certification.

## Next engineering work

1. Test real pages, locators, mouse/keyboard input, events, and failure behavior across sync and async APIs.
2. Address type transparency, context-manager return objects, callbacks, and special methods (possibly via `wrapt`).
3. Implement a selective override registry only after reliable passthrough.

## Very low priority — quick maintenance (approx. 2 minutes)

- [ ] **P4 / cosmetic:** Update the GitHub repository's short **About** description when convenient; leave it unchanged for now. Suggested wording: `Opt-in forwarding middleware for Playwright Python, with method-level overrides planned.`
- This is not an engineering blocker, not an urgent task, and should not displace forwarding tests.

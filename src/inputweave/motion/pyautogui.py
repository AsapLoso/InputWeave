"""Opt-in PyAutoGUI movement preset powered by the established PyTweening library.

The native PyAutoGUI backend performs every move or drag. InputWeave only
supplies default duration and easing parameters through its override registry.
No new cursor-trajectory engine and no global PyAutoGUI setting mutations.
"""

from __future__ import annotations

from contextlib import contextmanager
import math
from collections.abc import Iterator
from typing import Any

from inputweave.overrides import get_override, register_override, unregister_override

_METHODS = ("moveTo", "moveRel", "dragTo", "dragRel")
_CURVES = frozenset({"linear", "easeInOutQuad", "easeInOutSine", "easeOutCubic"})


@contextmanager
def eased_pyautogui_moves(
    *, duration: float = 0.25, curve: str = "easeInOutSine"
) -> Iterator[None]:
    """Temporarily apply motion defaults for InputWeave PyAutoGUI move/drag calls.

    An explicit native duration or tween argument is always preserved.
    Registration is process-global; this scope is not thread-safe.
    """
    if (
        not isinstance(duration, (int, float))
        or not math.isfinite(duration)
        or duration < 0
    ):
        raise ValueError("duration must be a finite nonnegative number")
    if curve not in _CURVES:
        raise ValueError(f"curve must be one of: {', '.join(sorted(_CURVES))}")

    try:
        import pytweening
    except ImportError as exc:
        raise ImportError(
            "Install the motion extra: pip install 'inputweave[motion]'"
        ) from exc

    tween = getattr(pytweening, curve)
    labels = tuple(f"pyautogui.{method}" for method in _METHODS)
    previous = {label: get_override(label) for label in labels}

    def route(original: Any, *args: Any, **kwargs: Any) -> Any:
        kwargs = dict(kwargs)
        # PyAutoGUI move/drag signatures take duration as arg 3, tween as arg 4.
        if len(args) < 3:
            kwargs.setdefault("duration", duration)
        if len(args) < 4:
            kwargs.setdefault("tween", tween)
        return original(*args, **kwargs)

    for label in labels:
        register_override(label, route)
    try:
        yield
    finally:
        for label in labels:
            handler = previous[label]
            if handler is None:
                unregister_override(label)
            else:
                register_override(label, handler)

"""Tests for the library-backed motion preset, without a desktop display."""

import sys
import types

import pytest

from inputweave.motion import eased_pyautogui_moves


def fake_pyautogui(monkeypatch):
    import inputweave.pyautogui as adapter

    adapter._backend = None
    for name in ("moveTo", "moveRel", "dragTo", "dragRel"):
        adapter.__dict__.pop(name, None)

    backend = types.ModuleType("pyautogui")
    calls = []

    def movement(name):
        def run(x, y, duration=0, tween=None, **kwargs):
            calls.append((name, x, y, duration, tween, kwargs))
            return "native result"
        return run

    for name in ("moveTo", "moveRel", "dragTo", "dragRel"):
        setattr(backend, name, movement(name))
    monkeypatch.setitem(sys.modules, "pyautogui", backend)
    return adapter, calls


def test_motion_preset_delegates_and_restores(monkeypatch, capsys):
    adapter, calls = fake_pyautogui(monkeypatch)
    assert adapter.moveTo(1, 2) == "native result"
    assert "Unchanged feature: pyautogui.moveTo" in capsys.readouterr().out

    with eased_pyautogui_moves(duration=0.3, curve="easeInOutSine"):
        for method in ("moveTo", "moveRel", "dragTo", "dragRel"):
            assert getattr(adapter, method)(10, 20) == "native result"
            name, x, y, duration, tween, extra = calls[-1]
            assert name == method
            assert (x, y, duration) == (10, 20, 0.3)
            assert tween(0.5) == pytest.approx(0.5)
        assert "Unchanged feature" not in capsys.readouterr().out

        # Explicit native arguments take priority over the middleware default.
        assert adapter.moveTo(3, 4, 0.8, lambda t: t * t) == "native result"
        assert calls[-1][3] == 0.8
        assert calls[-1][4](0.5) == 0.25
        assert adapter.moveTo(5, 6, duration=0, tween=lambda t: t) == "native result"
        assert calls[-1][3] == 0

    assert adapter.moveTo(7, 8) == "native result"
    assert calls[-1][3] == 0
    assert "Unchanged feature: pyautogui.moveTo" in capsys.readouterr().out


def test_motion_preserves_existing_override(monkeypatch):
    from inputweave.overrides import get_override, register_override, unregister_override

    adapter, _ = fake_pyautogui(monkeypatch)
    def previous(original, *args, **kwargs):
        return "previous handler"

    register_override("pyautogui.moveTo", previous)
    try:
        with eased_pyautogui_moves():
            assert adapter.moveTo(1, 2) == "native result"
        assert get_override("pyautogui.moveTo") is previous
        assert adapter.moveTo(1, 2) == "previous handler"
    finally:
        unregister_override("pyautogui.moveTo")


def test_motion_restores_on_exception(monkeypatch):
    from inputweave.overrides import get_override
    fake_pyautogui(monkeypatch)
    with pytest.raises(RuntimeError):
        with eased_pyautogui_moves():
            assert get_override("pyautogui.moveTo") is not None
            raise RuntimeError("cancel")
    assert get_override("pyautogui.moveTo") is None


@pytest.mark.parametrize("duration", [-1, float("inf"), float("nan"), "slow"])
def test_bad_duration(duration):
    with pytest.raises(ValueError):
        with eased_pyautogui_moves(duration=duration):
            pass


def test_bad_curve():
    with pytest.raises(ValueError):
        with eased_pyautogui_moves(curve="unknown"):
            pass

"""In-process cases for veri/stop_modes.py, the mode list stop-requested.sh and stop-run.sh share."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def stop_modes():
    return importlib.import_module("veri.stop_modes")


def test_stop_modes_lists_three_modes_matches_them_exactly_and_names_them_from_the_list_read_at_call_time(
        monkeypatch, stop_modes):
    started = []
    for owner, attr in ((subprocess, "Popen"), (os, "system"), (os, "fork"), (os, "posix_spawn"),
                        (os, "execv"), (os, "execve")):
        monkeypatch.setattr(owner, attr, lambda *a, _n=attr, **k: started.append(_n))

    assert stop_modes.STOP_MODES == ("at-ledger", "at-leaf", "now")
    known = {mode: stop_modes.stop_mode_known(mode)
             for mode in ("at-ledger", "at-leaf", "now", "Now", "now ", " now", "now\r", "", "at-step")}
    assert known == {"at-ledger": True, "at-leaf": True, "now": True, "Now": False, "now ": False,
                     " now": False, "now\r": False, "": False, "at-step": False}
    for mode in ("*", "now*", "[n]ow", "\x00", "now\nnow", b"\xff".decode("utf-8", "surrogateescape")):
        assert stop_modes.stop_mode_known(mode) is False, repr(mode)
    assert stop_modes.modes_named() == "at-ledger, at-leaf or now"

    monkeypatch.setattr(stop_modes, "STOP_MODES", ("now",))
    assert stop_modes.modes_named() == " or now"

    monkeypatch.setattr(stop_modes, "STOP_MODES", ("at-ledger", "at-leaf", "now", "at-step"))
    assert stop_modes.modes_named() == "at-ledger, at-leaf, now or at-step"
    assert stop_modes.stop_mode_known("at-step") is True
    assert started == []

"""In-process cases for veri/event.py, the module event.sh is a shim over."""
import importlib
import os
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: event.sh <event> [key=value …]\n".encode()
REASONS = b"candidates-done, budget-spent, nothing-structural"


@pytest.fixture
def event():
    return importlib.import_module("veri.event")


def test_main_refuses_a_missing_event_and_each_bad_structural_pass_with_exit_2_creating_no_tdd_and_accepts_a_plain_mark(
        monkeypatch, tmp_path, capsysbinary, event):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)

    refusals = []
    for argv in ([], [""],
                 ["structural-pass", "stopped=test-files-only"],
                 ["structural-pass", "transforms=0"],
                 ["structural-pass", "transforms=0", "budget=10", "stopped=budget-spent"]):
        code = event.main(argv)
        refusals.append((argv, code, capsysbinary.readouterr(), sorted(os.listdir(tmp_path))))

    assert refusals == [
        ([], 2, (b"", USAGE), []),
        ([""], 2, (b"", USAGE), []),
        (["structural-pass", "stopped=test-files-only"], 2,
         (b"", b"event.sh: structural-pass stopped=test-files-only is not one of " + REASONS + b"\n"), []),
        (["structural-pass", "transforms=0"], 2,
         (b"", b"event.sh: structural-pass needs stopped=, one of " + REASONS + b"\n"), []),
        (["structural-pass", "transforms=0", "budget=10", "stopped=budget-spent"], 2,
         (b"", b"event.sh: structural-pass stopped=budget-spent needs transforms equal to budget,"
               b" got transforms=0 budget=10\n"), []),
    ]
    assert event.main(["x"]) == 0

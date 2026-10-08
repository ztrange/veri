"""In-process cases for veri/event.py, the module event.sh is a shim over."""
import importlib
import json
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


CONTEXT = ("VERI_ISSUE", "VERI_ACTOR", "VERI_PHASE", "VERI_STEP", "VERI_ATTEMPT", "VERI_SKILL_COMMIT")


def test_main_appends_the_nine_fixed_keys_then_one_key_per_argument_in_argument_order(
        monkeypatch, tmp_path, event):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.clock_gettime", lambda clock: 4242.7)

    def context(values):
        for name, value in zip(CONTEXT, values):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)

    for values, argv in (
            (("12", "conductor", "red", "3", "2", "abc123"),
             ["launch", "z=1", "a=2", "a=3", "issue=9", "bare", "a=b=c", "=x", "k="]),
            ((None,) * 6, ["-h"]),
            (("",) * 6, ["mark"]),
    ):
        context(values)
        assert event.main(argv) == 0

    assert (tmp_path / ".tdd" / "events.jsonl").read_bytes() == (
        b'{"ts": 1700000000, "awake": 4242, "issue": "12", "actor": "conductor", "phase": "red",'
        b' "step": "3", "event": "launch", "attempt": "2", "skill_commit": "abc123",'
        b' "z": "1", "a": "2", "a": "3", "issue": "9", "bare": "", "a": "b=c", "": "x", "k": ""}\n'
        b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "", "phase": "", "step": "",'
        b' "event": "-h", "attempt": "", "skill_commit": ""}\n'
        b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "", "phase": "", "step": "",'
        b' "event": "mark", "attempt": "", "skill_commit": ""}\n'
    )


def test_main_escapes_every_string_by_the_bash_table_over_the_argument_and_variable_bytes(
        monkeypatch, tmp_path, event):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VERI_AWAKE_CLOCK", raising=False)
    monkeypatch.setattr("time.time", lambda: 1700000000.9)
    monkeypatch.setattr("time.clock_gettime", lambda clock: 4242.7)
    for name in CONTEXT:
        monkeypatch.delenv(name, raising=False)

    well = "\"\\\b\f\n\r\t\x01\x1f\x7fAé€\U0001F600"
    well_escaped = b'\\"\\\\\\b\\f\\n\\r\\t\\u0001\\u001f\\u007fA\\u00e9\\u20ac\\ud83d\\ude00'
    malformed = os.fsdecode(b"\x80|\xe2\x82Z")
    malformed_escaped = b"\\u0080|\\u209a"
    monkeypatch.setenv("VERI_ACTOR", well)
    monkeypatch.setenv("VERI_PHASE", malformed)

    assert well_escaped == json.dumps(well, ensure_ascii=True)[1:-1].encode()
    assert event.main([well, "w=" + well, "m=" + malformed, 'q"k=v']) == 0

    assert (tmp_path / ".tdd" / "events.jsonl").read_bytes() == (
        b'{"ts": 1700000000, "awake": 4242, "issue": "", "actor": "' + well_escaped
        + b'", "phase": "' + malformed_escaped + b'", "step": "", "event": "' + well_escaped
        + b'", "attempt": "", "skill_commit": "", "w": "' + well_escaped
        + b'", "m": "' + malformed_escaped + b'", "q\\"k": "v"}\n'
    )

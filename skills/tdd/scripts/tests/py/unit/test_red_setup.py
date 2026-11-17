"""In-process cases for veri/red_setup.py, the module red-setup.sh is a shim over."""
import importlib
import json

import pytest

LEDGER = ("# Plan for #7 — frob\n\n"
          "- [x] zorblat frobs a nitz ⟦criterion 1⟧\n"
          "- [ ] zorblat refuses an empty nitz ⟦criterion 2⟧\n")
REPORT = "TEST_PATH: tests/test_z.py\nPREDICTION: MATCHED\nSETUP: 4 | a fake clock, a stub gh, a tmp repo, a spy\n"


@pytest.fixture
def red_setup():
    return importlib.import_module("veri.red_setup")


def _run(tmp_path, ledger=LEDGER):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    if ledger is not None:
        (tmp_path / ".tdd" / "issue-7.md").write_text(ledger)
    return tmp_path


def _events(tmp_path):
    journal = tmp_path / ".tdd" / "events.jsonl"
    if not journal.exists():
        return []
    return [{k: e[k] for k in ("event", "issue", "step", "count", "what") if k in e}
            for e in map(json.loads, journal.read_text().splitlines())]


def test_record_writes_a_red_setup_event_for_the_ledgers_current_step_from_the_reports_setup_line_and_exits_0(
        tmp_path, run_cli, red_setup):
    code, _, err = run_cli(red_setup, ["record", "7"], stdin=REPORT, cwd=_run(tmp_path))

    assert (code, err, _events(tmp_path)) == (0, "", [
        {"event": "red-setup", "issue": "7", "step": "zorblat refuses an empty nitz ⟦criterion 2⟧", "count": "4",
         "what": "a fake clock, a stub gh, a tmp repo, a spy"}])


def test_record_exits_3_and_writes_nothing_when_the_report_has_no_setup_line(tmp_path, run_cli, red_setup):
    code, _, err = run_cli(red_setup, ["record", "7"], stdin="TEST_PATH: tests/test_z.py\nPREDICTION: MATCHED\n",
                           cwd=_run(tmp_path))

    assert (code, err, _events(tmp_path)) == (3, "", [])


@pytest.mark.parametrize("line", ["SETUP: four | a fake clock", "SETUP: 4 a fake clock", "SETUP: -1 | a spy", "SETUP:"])
def test_record_exits_2_with_one_stderr_line_and_writes_nothing_on_a_malformed_setup_line(
        tmp_path, run_cli, red_setup, line):
    code, _, err = run_cli(red_setup, ["record", "7"], stdin="PREDICTION: MATCHED\n" + line + "\n", cwd=_run(tmp_path))

    assert (code, len(err.splitlines()), err.startswith("red-setup: malformed SETUP: line"), _events(tmp_path)) == (
        2, 1, True, [])


@pytest.mark.parametrize("ledger, said", [
    ("# Plan for #7 — frob\n\n- [x] zorblat frobs a nitz ⟦criterion 1⟧\n", "red-setup: the ledger of #7 has no current step"),
    (None, "red-setup: cannot read the ledger of #7")])
def test_record_exits_2_with_one_stderr_line_and_writes_nothing_when_the_ledger_has_no_current_step(
        tmp_path, run_cli, red_setup, ledger, said):
    code, _, err = run_cli(red_setup, ["record", "7"], stdin=REPORT, cwd=_run(tmp_path, ledger))

    assert (code, len(err.splitlines()), err.startswith(said), _events(tmp_path)) == (2, 1, True, [])

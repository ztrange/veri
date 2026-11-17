"""In-process cases for veri/red_setup.py, the module red-setup.sh is a shim over."""
import importlib
import json
import os

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


def _journal(tmp_path, *marks):
    """A run whose journal holds a red-setup event per (issue, step, count, what), in order."""
    _run(tmp_path)
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(
        json.dumps({"ts": 1, "event": "red-setup", "issue": issue, "step": step, "count": count, "what": what}) + "\n"
        for issue, step, count, what in marks))
    return tmp_path


def _worst(run_cli, red_setup, tmp_path, env=None):
    owed = tmp_path / ".tdd" / "issue-7-refactor-owed.md"
    code, _, err = run_cli(red_setup, ["worst", "7", str(owed)], cwd=tmp_path, env=env)
    return code, err, owed.read_text() if owed.exists() else None


def test_worst_records_one_testability_row_for_the_step_whose_count_is_highest_over_the_threshold_and_exits_0(
        tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "2", "a spy"), ("7", "step two", "5", "a fake clock, a stub gh"),
             ("7", "step three", "4", "a tmp repo"))

    assert _worst(run_cli, red_setup, tmp_path) == (
        0, "", "not-done | testability | step two: 5 stubs and setup (a fake clock, a stub gh)\n")


@pytest.mark.parametrize("marks", [
    (("7", "step one", "3", "a spy, a stub, a fixture"), ("7", "step two", "1", "a spy")),
    (("8", "another run's step", "9", "nine fakes"),),
    ()])
def test_worst_exits_3_and_records_nothing_when_no_steps_count_exceeds_the_threshold(
        tmp_path, run_cli, red_setup, marks):
    _journal(tmp_path, *marks)

    assert _worst(run_cli, red_setup, tmp_path) == (3, "", None)


def test_worst_names_the_earliest_step_when_two_steps_tie_on_the_highest_count(tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "2", "a spy"), ("7", "step two", "6", "six fakes"),
             ("7", "step three", "6", "six other fakes"))

    assert _worst(run_cli, red_setup, tmp_path) == (
        0, "", "not-done | testability | step two: 6 stubs and setup (six fakes)\n")


def test_worst_reads_only_each_steps_latest_red_setup_count(tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "9", "nine fakes"), ("7", "step two", "5", "five fakes"),
             ("7", "step one", "1", "a spy"))

    assert _worst(run_cli, red_setup, tmp_path) == (
        0, "", "not-done | testability | step two: 5 stubs and setup (five fakes)\n")


def test_worst_run_a_second_time_replaces_its_own_row_and_keeps_the_owed_files_other_rows(
        tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "5", "five fakes"))
    owed = tmp_path / ".tdd" / "issue-7-refactor-owed.md"
    owed.write_text("### step one\n- extract the shared partial\n"
                    "not-done | testability | step zero: 4 stubs and setup (four fakes)\n"
                    "not-done | budget-spent | name the bounds walk once\n")

    assert _worst(run_cli, red_setup, tmp_path) == (
        0, "", "### step one\n- extract the shared partial\n"
               "not-done | budget-spent | name the bounds walk once\n"
               "not-done | testability | step one: 5 stubs and setup (five fakes)\n")



def test_worst_exits_2_with_a_stderr_line_when_the_owed_file_is_a_directory(tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "5", "five fakes"))
    owed = tmp_path / ".tdd" / "issue-7-refactor-owed.md"
    owed.mkdir()

    code, _, err = run_cli(red_setup, ["worst", "7", str(owed)], cwd=tmp_path)

    assert (code, len(err.splitlines()), err.startswith("red-setup: cannot rewrite " + str(owed))) == (2, 1, True)


def test_worst_exits_2_when_the_row_cannot_be_appended(tmp_path, run_cli, red_setup, monkeypatch):
    _journal(tmp_path, ("7", "step one", "5", "five fakes"))
    monkeypatch.setattr(red_setup.refactor_owed, "write", lambda file, text: 1)

    assert _worst(run_cli, red_setup, tmp_path)[0] == 2


def test_the_candidates_issue_lists_the_testability_row_worst_records_and_refactor_owed_list_never_prints_it(
        tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "5", "five fakes"))
    owed = tmp_path / ".tdd" / "issue-7-refactor-owed.md"
    owed.write_text("### step one\n- extract the shared partial\n")
    _worst(run_cli, red_setup, tmp_path)
    candidates = importlib.import_module("veri.refactor_candidates")
    refactor_owed = importlib.import_module("veri.refactor_owed")

    listed, out, _ = run_cli(refactor_owed, ["list", str(owed)])

    assert (candidates.grouped(owed.read_text()), listed, out) == (
        "## unsorted\n- testability | step one: 5 stubs and setup (five fakes)", 0, "extract the shared partial\n")


def test_worst_reads_its_threshold_from_veri_setup_threshold(tmp_path, run_cli, red_setup):
    _journal(tmp_path, ("7", "step one", "5", "five fakes"), ("7", "step two", "2", "a spy, a stub"))

    assert [_worst(run_cli, red_setup, tmp_path, env={"VERI_SETUP_THRESHOLD": value})[0] for value in ("5", "1")] == [3, 0]


@pytest.mark.parametrize("value", ["three", "-1", "2.5", " 3"])
def test_worst_exits_2_with_one_stderr_line_naming_the_knob_on_a_threshold_that_is_not_a_whole_number(
        tmp_path, run_cli, red_setup, value):
    _journal(tmp_path, ("7", "step one", "5", "five fakes"))

    code, err, owed = _worst(run_cli, red_setup, tmp_path, env={"VERI_SETUP_THRESHOLD": value})

    assert (code, len(err.splitlines()), "VERI_SETUP_THRESHOLD" in err, owed) == (2, 1, True, None)


def test_veri_setup_threshold_is_a_tunables_entry_reading_a_whole_number_default_3():
    tunables = importlib.import_module("veri.tunables")

    assert (tunables.default("VERI_SETUP_THRESHOLD"), tunables.parses("VERI_SETUP_THRESHOLD", "0"),
            tunables.parses("VERI_SETUP_THRESHOLD", "2.5")) == ("3", True, False)


def test_worst_records_a_row_carrying_no_local_path_of_the_run_or_the_home_directory(tmp_path, run_cli, red_setup):
    home = os.path.expanduser("~")
    _journal(tmp_path, ("7", "step one", "5", "a fixture at %s/f.json, a stub in %s/bin" % (tmp_path, home)))

    code, _, owed = _worst(run_cli, red_setup, tmp_path)

    assert (code, str(tmp_path) in owed, home in owed, owed.startswith("not-done | testability | step one: 5")) == (
        0, False, False, True)

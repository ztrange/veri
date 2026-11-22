"""In-process rerecord-approved cases, on a history committed through fed_commits (#4642).

A human approved re-recording named stale cases: `tests-frozen.sh rerecord-approved <ledger> --approval <text> <case>...`
re-records exactly those cases at their HEAD bodies, each with its `helpers:` line, and leaves every other record line
byte-identical. Every commit goes through fed_commits, so case_history answers HEAD's text from the fed log.
"""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# The plan repository: ledger .tdd/issue-9.md (VERI_ISSUE=9) over STEPS. Names, not literals, in calls: a literal
# suite path reads as a nested run.
STEPS = ["step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"
SUITE = "test_suite.py"
PLAN_LEDGER = ".tdd/issue-9.md"


def _ledger(root, a):
    (root / PLAN_LEDGER).write_text("- [%s] %s\n- [ ] %s\n" % (a, STEPS[0], STEPS[1]))


def test_rerecord_approved_re_records_only_the_named_stale_case_and_check_earlier_still_refuses_the_other_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    monkeypatch.setenv("VERI_ISSUE", "9")
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / SUITE
    suite.write_text(CASE % ("base", 0))
    _ledger(tmp_path, " ")
    repo = fed_commits(root=tmp_path)
    repo.add(SUITE, PLAN_LEDGER)
    repo.commit("plan")
    suite.write_text(CASE % ("one", 1) + "\n\n" + CASE % ("two", 2))
    run_cli(tests_frozen, ["record", "--step", STEPS[0], SUITE], cwd=tmp_path)
    _ledger(tmp_path, "x")
    repo.commit("A green", all=True)
    suite.write_text(CASE % ("one", 10) + "\n\n" + CASE % ("two", 20))
    repo.commit("edit both cases", all=True)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    before = record.read_text().splitlines()

    code = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "the human said so", "test_one"],
                   cwd=tmp_path)[0]
    after = record.read_text().splitlines()
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[1]], cwd=tmp_path)[:2]

    untouched = lambda lines: [l for l in lines if "\ttest_one\t" not in l]
    assert (code, untouched(after) == untouched(before), after != before, checked) == (
        0, True, True, (1, "test_two (%s)\n" % STEPS[0]))

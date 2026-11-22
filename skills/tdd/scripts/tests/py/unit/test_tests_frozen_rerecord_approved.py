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


GO_SUITE = "suite_test.go"
VERDICT = ".tdd/verdict-refactor.exit"


def _step_a(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, path, recorded):
    """The plan repository, then step A recording `recorded` in `path` and ticking itself; returns (repo, green)."""
    monkeypatch.setenv("VERI_ISSUE", "9")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / SUITE).write_text(CASE % ("base", 0))
    _ledger(tmp_path, " ")
    repo = fed_commits(root=tmp_path)
    repo.add(SUITE, PLAN_LEDGER)
    repo.commit("plan")
    (tmp_path / path).write_text(recorded)
    repo.add(path)
    run_cli(tests_frozen, ["record", "--step", STEPS[0], path], cwd=tmp_path)
    _ledger(tmp_path, "x")
    return repo, repo.commit("A green", all=True)


def test_rerecord_approved_re_records_a_case_rerecord_refactored_skipped_for_its_moved_helper_lines_so_check_earlier_passes_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + chk("c") + '}\n'
    moved = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
             'func check(t *testing.T, x int) {\n' + chk("a") + '}\n')
    repo, green = _step_a(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, GO_SUITE, inline)
    (tmp_path / GO_SUITE).write_text(moved)
    repo.commit("A refactor", all=True)
    (tmp_path / VERDICT).write_text("0")
    skipped = run_cli(tests_frozen, ["rerecord-refactored", PLAN_LEDGER, green], cwd=tmp_path)[0]

    code = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "keep it", "TestOne"],
                   cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", PLAN_LEDGER, "--step", STEPS[1]], cwd=tmp_path)[:2]

    assert (skipped, code, checked) == (1, 0, (0, ""))


def _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    """Step A records test_one and test_two, a later commit edits both; returns (repo, the record file)."""
    repo = _step_a(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, SUITE,
                   CASE % ("one", 1) + "\n\n" + CASE % ("two", 2))[0]
    (tmp_path / SUITE).write_text(CASE % ("one", 10) + "\n\n" + CASE % ("two", 20))
    repo.commit("edit both cases", all=True)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    return repo, record


def test_rerecord_approved_naming_a_case_no_record_holds_exits_2_naming_it_and_writes_nothing_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    record = _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)[1]
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "yes", "test_one",
                                          "test_nowhere"], cwd=tmp_path)

    assert (code, "test_nowhere" in err, record.read_bytes() == before) == (2, True, True)


def test_rerecord_approved_naming_no_case_exits_2_with_the_usage_and_writes_nothing_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    record = _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)[1]
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "yes"], cwd=tmp_path)

    assert (code, "rerecord-approved <ledger>" in err, record.read_bytes() == before) == (2, True, True)


def test_rerecord_approved_naming_a_recorded_case_absent_at_head_exits_2_naming_it_and_writes_nothing_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    repo, record = _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    (tmp_path / SUITE).write_text(CASE % ("two", 20))
    repo.commit("delete test_one", all=True)
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "yes", "test_two",
                                          "test_one"], cwd=tmp_path)

    assert (code, "test_one" in err, record.read_bytes() == before) == (2, True, True)

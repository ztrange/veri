"""In-process rerecord-approved cases, on a history committed through fed_commits (#4642).

A human approved re-recording named stale cases: `tests-frozen.sh rerecord-approved <ledger> --approval <text> <case>...`
re-records exactly those cases at their HEAD bodies, each with its `helpers:` line, and leaves every other record line
byte-identical. Every commit goes through fed_commits, so case_history answers HEAD's text from the fed log.
"""
import importlib
import json
from pathlib import Path

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

    def untouched(lines):
        return [l for l in lines if "\ttest_one\t" not in l]
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
    def chk(m):
        return '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
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


def test_rerecord_approved_whose_second_record_cannot_be_written_exits_2_and_restores_the_first_byte_identical_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    first = _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)[1]
    second = tmp_path / tests_frozen.record_path(STEPS[1])
    second.write_bytes(first.read_bytes())
    (tmp_path / PLAN_LEDGER).write_text("- [x] %s\n- [x] %s\n" % tuple(STEPS))
    before = (first.read_bytes(), second.read_bytes())
    real_open = open

    def refusing_open(path, mode="r", *args, **kwargs):
        if "w" in mode and str(path).endswith(second.name):
            raise OSError("read-only record")
        return real_open(path, mode, *args, **kwargs)
    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)

    code = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "yes", "test_one"], cwd=tmp_path)[0]

    assert (code, first.read_bytes() == before[0], second.read_bytes() == before[1]) == (2, True, True)


def _approved_events(tmp_path):
    journal = tmp_path / ".tdd" / "events.jsonl"
    lines = journal.read_text().splitlines() if journal.exists() else []
    return sorted((e["case"], e["file"], e["approval"]) for e in map(json.loads, filter(str.strip, lines))
                  if e["event"] == "tests-frozen-rerecord-approved")


def test_rerecord_approved_re_recording_two_cases_logs_one_event_per_case_with_its_file_and_the_approval_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)

    code = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "the human: re-record both", "test_one",
                                  "test_two"], cwd=tmp_path)[0]

    assert (code, _approved_events(tmp_path)) == (0, [("test_one", SUITE, "the human: re-record both"),
                                                     ("test_two", SUITE, "the human: re-record both")])


@pytest.mark.parametrize("approval", [[], ["--approval", ""]], ids=["missing", "empty"])
def test_rerecord_approved_without_the_approval_text_exits_2_with_the_usage_and_writes_no_record_or_event_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits, approval):
    record = _two_stale(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)[1]
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER] + approval + ["test_one"], cwd=tmp_path)

    assert (code, "rerecord-approved <ledger> --approval" in err, record.read_bytes() == before,
            _approved_events(tmp_path)) == (2, True, True, [])


def test_tests_frozen_usage_text_names_the_rerecord_approved_verb_4642(run_cli, tests_frozen):
    code, _, err = run_cli(tests_frozen, [])

    assert (code, "rerecord-approved" in err) == (2, True)


def test_rerecord_approved_is_named_with_its_arguments_and_event_in_the_shim_header_and_scripts_md_4642():
    scripts = Path(__file__).resolve().parents[3]
    header = (scripts / "tests-frozen.sh").read_text().split("\nexec ")[0]
    entry = [line for line in (scripts.parent / "SCRIPTS.md").read_text().splitlines()
             if line.startswith("- `$S/tests-frozen.sh ")][0]

    assert ["tests-frozen.sh rerecord-approved <ledger> --approval <text> <case>..." in header,
            "rerecord-approved <ledger> --approval <text> <case>..." in entry,
            "tests-frozen-rerecord-approved" in header, "tests-frozen-rerecord-approved" in entry] == [True] * 4


OTHER = "other_suite.py"


def _same_case_in_two_files(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    """Step A records test_one in SUITE and in OTHER, a later commit edits both; returns the record file."""
    monkeypatch.setenv("VERI_ISSUE", "9")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / SUITE).write_text(CASE % ("base", 0))
    _ledger(tmp_path, " ")
    repo = fed_commits(root=tmp_path)
    repo.add(SUITE, PLAN_LEDGER)
    repo.commit("plan")
    for path in (SUITE, OTHER):
        (tmp_path / path).write_text(CASE % ("one", 1))
    repo.add(OTHER)
    run_cli(tests_frozen, ["record", "--step", STEPS[0], SUITE, OTHER], cwd=tmp_path)
    _ledger(tmp_path, "x")
    repo.commit("A green", all=True)
    for path in (SUITE, OTHER):
        (tmp_path / path).write_text(CASE % ("one", 10))
    repo.commit("edit both files", all=True)
    return next((tmp_path / ".tdd").glob("tests-frozen-*.record"))


def test_rerecord_approved_file_double_colon_case_re_records_only_that_files_case_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    record = _same_case_in_two_files(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    before = record.read_text().splitlines()

    code = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "yes", SUITE + "::test_one"],
                   cwd=tmp_path)[0]
    after = record.read_text().splitlines()

    def other(lines):
        return [l for l in lines if ": %s\t" % OTHER in l]
    changed = [l for l in after if l not in before]
    assert (code, other(after) == other(before), bool(changed), all(": %s\t" % SUITE in l for l in changed)) == (
        0, True, True, True)


def test_rerecord_approved_bare_case_name_matching_two_recorded_cases_exits_2_naming_both_and_writes_nothing_4642(
        tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits):
    record = _same_case_in_two_files(tmp_path, run_cli, tests_frozen, monkeypatch, fed_commits)
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-approved", PLAN_LEDGER, "--approval", "yes", "test_one"],
                           cwd=tmp_path)

    assert (code, SUITE + "::test_one" in err, OTHER + "::test_one" in err, record.read_bytes() == before) == (
        2, True, True, True)

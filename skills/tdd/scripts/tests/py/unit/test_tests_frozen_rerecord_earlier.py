"""In-process rerecord-earlier cases on a history committed through fed_commits (PRD 017.9)."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
SUITE = "tests/test_suite.py"
GO_SUITE = "suite_test.go"
LEDGER = ".tdd/ledger.md"
OLDER = "def test_older_case():\n    assert True\n"
PINNED = OLDER + "\n\ndef test_pinned_2199():\n    assert %s\n"
STEPS = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"


def _based(root, fed_commits, branch="main", also=()):
    """root holding tests/ and .tdd/, the suite holding OLDER committed as "base" with the files `also` names; returns
    the fed_commits log."""
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / ".tdd").mkdir()
    (root / SUITE).write_text(OLDER)
    repo = fed_commits(root=root, branch=branch)
    repo.add("tests", *also)
    repo.commit("base")
    return repo


def _diff_checked_repo(tmp_path, run_cli, tests_frozen, fed_commits, commit_ledger=True):
    """Step one records test_pinned_2199, the ledger ticks it and the diff-checked step two, which edits the case."""
    repo = _based(tmp_path, fed_commits)
    (tmp_path / SUITE).write_text(PINNED % "1 == 2")
    run_cli(tests_frozen, ["record", "--step", STEPS[0], SUITE], cwd=tmp_path)
    repo.add("tests")
    repo.commit("red")
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % STEPS)
    if commit_ledger:
        repo.add(LEDGER)
        repo.commit("ledger")
    (tmp_path / SUITE).write_text(PINNED % "2 == 2")
    repo.add("tests")
    repo.commit("edit")
    return ledger, STEPS


def test_rerecord_earlier_derives_the_step_base_from_its_own_commits_so_a_later_plan_commit_neither_empties_the_diff_nor_blocks_the_rewrite_3468(
        tmp_path, run_cli, tests_frozen, fed_commits):
    earlier, edit, later = STEPS
    pinned = OLDER + "\n\ndef test_pinned_3468():\n    assert %s\n"

    def build(name, edited):
        root = tmp_path / name
        (root / "notes.txt").parent.mkdir(parents=True)
        (root / "notes.txt").write_text("a\n")
        repo = _based(root, fed_commits, branch="tdd/9-x", also=["notes.txt"])
        (root / SUITE).write_text(pinned % "1 == 2")
        run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=root)
        ledger = root / ".tdd/issue-9.md"
        ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
        repo.add("tests", ".tdd/issue-9.md")
        repo.commit("red")
        if edited:
            (root / SUITE).write_text(pinned % "2 == 2")
        else:
            (root / "notes.txt").write_text("b\n")
        repo.add("tests", "notes.txt")
        repo.commit("edit")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
        repo.add(".tdd/issue-9.md")
        repo.commit("tick")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n- [ ] step four\n" % (earlier, edit, later))
        repo.add(".tdd/issue-9.md")
        repo.commit("plan: rewrite")
        record = root / run_cli(tests_frozen, ["path", earlier], cwd=root)[1].strip()
        return root, ledger, record

    results = []
    for name, edited in (("changed", True), ("unchanged", False)):
        root, ledger, record = build(name, edited)
        before = record.read_bytes()
        code = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=root,
                       env={"VERI_ISSUE": "9"})[0]
        results.append((code, record.read_bytes() != before))

    assert results == [(0, True), (0, False)]


def test_rerecord_earlier_derives_the_step_base_from_its_own_commits_when_an_earlier_plan_commit_introduced_the_step_line_3468(
        tmp_path, run_cli, tests_frozen, fed_commits):
    earlier, edit, later = STEPS
    pinned = OLDER + "\n\ndef test_pinned_3468():\n    assert %s\n"

    def build(name, edited):
        root = tmp_path / name
        (root / "notes.txt").parent.mkdir(parents=True)
        (root / "notes.txt").write_text("a\n")
        repo = _based(root, fed_commits, branch="tdd/9-x", also=["notes.txt"])
        ledger = root / ".tdd/issue-9.md"
        ledger.write_text("- [ ] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
        repo.add(".tdd/issue-9.md")
        repo.commit("plan: scope")
        (root / SUITE).write_text(pinned % "1 == 2")
        run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=root)
        repo.add("tests")
        repo.commit("red")
        if edited:
            (root / SUITE).write_text(pinned % "2 == 2")
        else:
            (root / "notes.txt").write_text("b\n")
        repo.add("tests", "notes.txt")
        repo.commit("edit")
        ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
        repo.add(".tdd/issue-9.md")
        repo.commit("plan: drop step two")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
        repo.add(".tdd/issue-9.md")
        repo.commit("plan: re-add step two")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n- [ ] step four\n" % (earlier, edit, later))
        repo.add(".tdd/issue-9.md")
        repo.commit("plan: rewrite")
        record = root / run_cli(tests_frozen, ["path", earlier], cwd=root)[1].strip()
        return root, ledger, record

    results = []
    for name, edited in (("changed", True), ("unchanged", False)):
        root, ledger, record = build(name, edited)
        before = record.read_bytes()
        code = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=root,
                       env={"VERI_ISSUE": "9"})[0]
        results.append((code, record.read_bytes() != before))

    assert results == [(0, True), (0, False)]


def test_rerecord_earlier_keeps_the_record_of_a_case_edited_in_a_commit_before_the_step_base_and_check_earlier_names_it_2199(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = _based(tmp_path, fed_commits)
    earlier, edit, later = STEPS
    (tmp_path / SUITE).write_text(PINNED % "1 == 2")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    repo.add("tests")
    repo.commit("red")
    (tmp_path / SUITE).write_text(PINNED % "2 == 2")
    repo.add("tests")
    repo.commit("edit before the step base")
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    repo.add(LEDGER)
    repo.commit("ledger")

    run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (code, "test_pinned_2199 (%s)" % earlier in out) == (1, True)


def test_rerecord_earlier_leaves_the_ticked_steps_own_record_byte_for_byte_and_rewrites_the_earlier_steps_2199(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = _based(tmp_path, fed_commits)
    earlier, edit = STEPS[:2]
    (tmp_path / SUITE).write_text(PINNED % "1 == 2")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    repo.add("tests")
    repo.commit("red")
    paths = [Path(run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()) for step in (earlier, edit)]
    paths = [p if p.is_absolute() else tmp_path / p for p in paths]
    paths[1].write_text(paths[0].read_text())
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n" % (earlier, edit))
    repo.add(".tdd")
    repo.commit("ledger")
    (tmp_path / SUITE).write_text(PINNED % "2 == 2")
    repo.add("tests")
    repo.commit("edit")
    own_before, earlier_before = paths[1].read_bytes(), paths[0].read_bytes()

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]

    assert (rerecorded, paths[1].read_bytes() == own_before, paths[0].read_bytes() != earlier_before) == (0, True, True)


def test_rerecord_earlier_keeps_the_record_of_a_frozen_case_edited_only_in_the_working_tree_2199(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = _based(tmp_path, fed_commits)
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 6⟧", "step three adds another"
    (tmp_path / SUITE).write_text(PINNED % "1 == 2")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    repo.add("tests")
    repo.commit("red")
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    repo.add(LEDGER)
    repo.commit("ledger")
    (tmp_path / SUITE).write_text(PINNED % "2 == 2")

    run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (code, "test_pinned_2199 (%s)" % earlier in out) == (1, True)


def test_rerecord_earlier_run_from_a_subdirectory_with_a_relative_ledger_path_rewrites_the_changed_case_2199(
        tmp_path, run_cli, tests_frozen, fed_commits):
    ledger, (_, edit, later) = _diff_checked_repo(tmp_path, run_cli, tests_frozen, fed_commits)

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", "../" + LEDGER, "--step", edit],
                         cwd=tmp_path / "tests")[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, out) == (0, 0, "")


def test_rerecord_earlier_with_a_ledger_no_commit_touched_is_exit_2_and_rewrites_no_record_2199(
        tmp_path, run_cli, tests_frozen, fed_commits):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen, fed_commits, commit_ledger=False)
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)

    assert (code, record.read_bytes() == before, "ledger" in err) == (2, True, True)


def test_rerecord_earlier_when_git_show_fails_on_a_recorded_file_is_exit_2_not_read_as_no_cases_2199(
        tmp_path, run_cli, tests_frozen, fed_commits, monkeypatch):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen, fed_commits)
    history = tests_frozen.case_history
    readable = history.cases_at

    def corrupted_at_head(rev, path):
        """As git show fails on HEAD's corrupted blob of the suite, at every revision naming HEAD's commit:
        case_history raises, naming rev and path."""
        if path == SUITE and history.commit_of(rev) == history.commit_of("HEAD"):
            raise OSError("git show %s:%s failed: error: inflate: data stream error" % (rev, path))
        return readable(rev, path)

    monkeypatch.setattr(history, "cases_at", corrupted_at_head)
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)

    assert (code, record.read_bytes() == before, SUITE in err) == (2, True, True)


def test_rerecord_earlier_returns_2_naming_the_record_when_writing_it_raises_2199(
        tmp_path, run_cli, tests_frozen, fed_commits, monkeypatch, capfd):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen, fed_commits)
    record = run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(tmp_path)

    code = tests_frozen.rerecord_earlier(str(ledger), edit)

    assert (code, record in capfd.readouterr().err) == (2, True)


def test_rerecord_earlier_leaves_one_helpers_line_from_head_for_a_go_case_whose_record_held_two_stale_ones_so_check_earlier_exits_0_2998(
        tmp_path, run_cli, tests_frozen, fed_commits):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / GO_SUITE
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    repo = fed_commits()
    (tmp_path / "base.txt").write_text("base\n")
    repo.add("base.txt")
    repo.commit("base")
    earlier, edit, later = STEPS
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    run_cli(tests_frozen, ["record", "--step", earlier, GO_SUITE], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line + stale if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    repo.add(GO_SUITE)
    repo.commit("red")
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    repo.add(LEDGER)
    repo.commit("ledger")
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    repo.add(GO_SUITE)
    repo.commit("edit moves the assertions into a helper")
    held = tests_frozen._helper_digest(suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0])

    run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)[:2]

    assert ([line for line in record.read_text().splitlines() if line.startswith("helpers: ")], checked) == (
        ["helpers: suite_test.go\tTestX\t%s" % held], (0, ""))


def test_rerecord_earlier_rewrites_body_and_helpers_lines_together_from_head_when_a_diff_checked_step_makes_a_case_call_a_new_helper_3052(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = _based(tmp_path, fed_commits)
    suite = tmp_path / SUITE
    earlier, edit, later = STEPS
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef check_old(x):\n    assert x == 1\n\n\n"
                     "def test_pinned_3052():\n    check_old(1)\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    repo.add("tests")
    repo.commit("red")
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    repo.add(LEDGER)
    repo.commit("ledger")
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef check_new(x):\n    assert x == 1\n    assert x < 2\n\n\n"
                     "def test_pinned_3052():\n    check_new(1)\n")
    repo.add("tests")
    repo.commit("edit makes the case call a new helper")
    text = suite.read_text()
    head = tests_frozen._helper_digest(text, tests_frozen._bodies_of(text, "test_pinned_3052")[0])

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    held = [line.split("\t")[-1] for line in record.read_text().splitlines() if line.startswith("helpers: ")]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, held, code, out) == (0, [head], 0, "")


def test_rerecord_earlier_leaves_no_helpers_line_for_a_case_that_calls_no_helper_at_head_3052(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = _based(tmp_path, fed_commits)
    suite = tmp_path / SUITE
    earlier, edit, later = STEPS
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef check_old(x):\n    assert x == 1\n\n\n"
                     "def test_pinned_3052():\n    check_old(1)\n")
    run_cli(tests_frozen, ["record", "--step", earlier, SUITE], cwd=tmp_path)
    repo.add("tests")
    repo.commit("red")
    ledger = tmp_path / LEDGER
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    repo.add(LEDGER)
    repo.commit("ledger")
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_pinned_3052():\n    assert 1 == 1\n")
    repo.add("tests")
    repo.commit("edit makes the case call no helper")

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    held = [line for line in record.read_text().splitlines() if line.startswith("helpers: ")]

    assert (rerecorded, held) == (0, [])

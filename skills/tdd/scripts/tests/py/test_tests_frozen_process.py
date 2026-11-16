"""Cases for veri/tests_frozen.py that run git in a real repository under tmp_path."""
import importlib
from pathlib import Path
import subprocess
import sys

import pytest

from conftest import receipt_leaver
from repo_builder import new_repo


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


def git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                   capture_output=True)


@pytest.mark.process("a real git repository under tmp_path, asked for HEAD and the work tree's content")
def test_check_earlier_pass_marker_differs_after_a_work_tree_edit_and_is_the_same_without_one_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    (tmp_path / "lib.py").write_text("one\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests", "lib.py")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    argv = ["check-earlier", str(ledger), "--step", current]

    def marker():
        code = run_cli(tests_frozen, argv, cwd=tmp_path)[0]
        (path,) = (tmp_path / ".tdd").glob("check-earlier-*.pass")
        return code, path.read_text()

    first = marker()
    again = marker()
    (tmp_path / "lib.py").write_text("two\n")
    edited = marker()
    (tmp_path / "notes.txt").write_text("untracked\n")
    untracked = marker()

    assert [first[0], again[0], edited[0], untracked[0]] == [0, 0, 0, 0]
    assert first[1] == again[1]
    assert len({first[1], edited[1], untracked[1]}) == 3
    assert "step: %s\nhead: " % current in edited[1]


@pytest.mark.process("a real git repository under tmp_path holding a nested repository made by new_repo")
def test_check_earlier_exits_2_naming_the_work_tree_hash_and_writes_no_pass_marker_for_an_untracked_nested_repo_with_no_commits_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    (tmp_path / "nested").mkdir()
    new_repo(tmp_path / "nested")

    code, out, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, out, "work-tree hash" in err, list((tmp_path / ".tdd").glob("check-earlier-*.pass"))) == (
        2, "", True, [])


@pytest.mark.process("a real git repository under tmp_path whose .gitignore lists .tdd/")
def test_check_earlier_exits_0_and_writes_a_pass_marker_when_the_repository_gitignores_tdd_2230(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    (tmp_path / ".gitignore").write_text(".tdd/\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests", ".gitignore")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, current = "step one adds a case", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, _, err = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=tmp_path)

    assert (code, len(list((tmp_path / ".tdd").glob("check-earlier-*.pass")))) == (0, 1), err


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_for_a_diff_checked_step_rewrites_the_changed_case_so_a_later_check_earlier_names_nothing_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, out) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, asked for the commits of a step and the file at HEAD")
def test_rerecord_earlier_derives_the_step_base_from_its_own_commits_so_a_later_plan_commit_neither_empties_the_diff_nor_blocks_the_rewrite_3468(
        tmp_path, run_cli, tests_frozen):
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    older = "def test_older_case():\n    assert True\n"
    pinned = older + "\n\ndef test_pinned_3468():\n    assert %s\n"

    def build(name, edited):
        repo = tmp_path / name
        (repo / "tests").mkdir(parents=True)
        (repo / ".tdd").mkdir()
        (repo / "tests/test_suite.py").write_text(older)
        (repo / "notes.txt").write_text("a\n")
        new_repo(repo, branch="tdd/9-x")
        git(repo, "add", "tests", "notes.txt")
        git(repo, "commit", "-q", "-m", "base")
        (repo / "tests/test_suite.py").write_text(pinned % "1 == 2")
        run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
        ledger = repo / ".tdd/issue-9.md"
        ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
        git(repo, "add", "tests", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "red")
        if edited:
            (repo / "tests/test_suite.py").write_text(pinned % "2 == 2")
        else:
            (repo / "notes.txt").write_text("b\n")
        git(repo, "add", "tests", "notes.txt")
        git(repo, "commit", "-q", "-m", "edit")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
        git(repo, "add", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "tick")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n- [ ] step four\n" % (earlier, edit, later))
        git(repo, "add", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "plan: rewrite")
        record = repo / run_cli(tests_frozen, ["path", earlier], cwd=repo)[1].strip()
        return repo, ledger, record

    results = []
    for name, edited in (("changed", True), ("unchanged", False)):
        repo, ledger, record = build(name, edited)
        before = record.read_bytes()
        code = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=repo,
                       env={"VERI_ISSUE": "9"})[0]
        results.append((code, record.read_bytes() != before))

    assert results == [(0, True), (0, False)]


@pytest.mark.process("a real git repository under tmp_path, asked for the commits of a step and the file at HEAD")
def test_rerecord_earlier_derives_the_step_base_from_its_own_commits_when_an_earlier_plan_commit_introduced_the_step_line_3468(
        tmp_path, run_cli, tests_frozen):
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    older = "def test_older_case():\n    assert True\n"
    pinned = older + "\n\ndef test_pinned_3468():\n    assert %s\n"

    def build(name, edited):
        repo = tmp_path / name
        (repo / "tests").mkdir(parents=True)
        (repo / ".tdd").mkdir()
        (repo / "tests/test_suite.py").write_text(older)
        (repo / "notes.txt").write_text("a\n")
        new_repo(repo, branch="tdd/9-x")
        git(repo, "add", "tests", "notes.txt")
        git(repo, "commit", "-q", "-m", "base")
        ledger = repo / ".tdd/issue-9.md"
        ledger.write_text("- [ ] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
        git(repo, "add", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "plan: scope")
        (repo / "tests/test_suite.py").write_text(pinned % "1 == 2")
        run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
        git(repo, "add", "tests")
        git(repo, "commit", "-q", "-m", "red")
        if edited:
            (repo / "tests/test_suite.py").write_text(pinned % "2 == 2")
        else:
            (repo / "notes.txt").write_text("b\n")
        git(repo, "add", "tests", "notes.txt")
        git(repo, "commit", "-q", "-m", "edit")
        ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, later))
        git(repo, "add", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "plan: drop step two")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
        git(repo, "add", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "plan: re-add step two")
        ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n- [ ] step four\n" % (earlier, edit, later))
        git(repo, "add", ".tdd/issue-9.md")
        git(repo, "commit", "-q", "-m", "plan: rewrite")
        record = repo / run_cli(tests_frozen, ["path", earlier], cwd=repo)[1].strip()
        return repo, ledger, record

    results = []
    for name, edited in (("changed", True), ("unchanged", False)):
        repo, ledger, record = build(name, edited)
        before = record.read_bytes()
        code = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=repo,
                       env={"VERI_ISSUE": "9"})[0]
        results.append((code, record.read_bytes() != before))

    assert results == [(0, True), (0, False)]


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_keeps_the_record_of_a_case_edited_in_a_commit_before_the_step_base_and_check_earlier_names_it_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit before the step base")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")

    run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (code, "test_pinned_2199 (%s)" % earlier in out) == (1, True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_leaves_the_ticked_steps_own_record_byte_for_byte_and_rewrites_the_earlier_steps_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    paths = [Path(run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()) for step in (earlier, edit)]
    paths = [p if p.is_absolute() else tmp_path / p for p in paths]
    paths[1].write_text(paths[0].read_text())
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n" % (earlier, edit))
    git(tmp_path, "add", ".tdd")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")
    own_before, earlier_before = paths[1].read_bytes(), paths[0].read_bytes()

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]

    assert (rerecorded, paths[1].read_bytes() == own_before, paths[0].read_bytes() != earlier_before) == (0, True, True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_keeps_the_record_of_a_frozen_case_edited_only_in_the_working_tree_2199(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 6⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", "-f", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")

    run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (code, "test_pinned_2199 (%s)" % earlier in out) == (1, True)


def _diff_checked_repo(tmp_path, run_cli, tests_frozen, commit_ledger=True):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    steps = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", steps[0], "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % steps)
    if commit_ledger:
        git(tmp_path, "add", "-f", ".tdd/ledger.md")
        git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")
    return ledger, steps


@pytest.mark.process("a real git repository under tmp_path, asked for the commit that last touched the ledger")
def test_rerecord_earlier_run_from_a_subdirectory_with_a_relative_ledger_path_rewrites_the_changed_case_2199(
        tmp_path, run_cli, tests_frozen):
    ledger, (_, edit, later) = _diff_checked_repo(tmp_path, run_cli, tests_frozen)

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", "../.tdd/ledger.md", "--step", edit],
                         cwd=tmp_path / "tests")[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, code, out) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, asked for the commit that last touched the ledger")
def test_rerecord_earlier_with_a_ledger_no_commit_touched_is_exit_2_and_rewrites_no_record_2199(
        tmp_path, run_cli, tests_frozen):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen, commit_ledger=False)
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)

    assert (code, record.read_bytes() == before, "ledger" in err) == (2, True, True)


@pytest.mark.process("a real git repository under tmp_path whose blob at HEAD is corrupted, so git show fails")
def test_rerecord_earlier_when_git_show_fails_on_a_recorded_file_is_exit_2_not_read_as_no_cases_2199(
        tmp_path, run_cli, tests_frozen):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen)
    blob = subprocess.run(["git", "rev-parse", "HEAD:tests/test_suite.py"], cwd=tmp_path, check=True,
                          capture_output=True, text=True).stdout.strip()
    loose = tmp_path / ".git/objects" / blob[:2] / blob[2:]
    loose.chmod(0o644)
    loose.write_bytes(b"not a zlib stream")
    record = tmp_path / run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)

    assert (code, record.read_bytes() == before, "tests/test_suite.py" in err) == (2, True, True)


@pytest.mark.process("a real git repository under tmp_path, the earlier record's write made to raise")
def test_rerecord_earlier_returns_2_naming_the_record_when_writing_it_raises_2199(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    ledger, (earlier, edit, _) = _diff_checked_repo(tmp_path, run_cli, tests_frozen)
    record = run_cli(tests_frozen, ["path", earlier], cwd=tmp_path)[1].strip()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(tmp_path)

    code = tests_frozen.rerecord_earlier(str(ledger), edit)

    assert (code, record in capfd.readouterr().err) == (2, True)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_re_records_an_earlier_case_changed_only_upstream_so_check_earlier_exits_0_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"
    stale = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]
    usage = run_cli(tests_frozen, [], cwd=repo)[2]

    assert (stale, code, after) == (1, 0, 0)
    assert "rerecord-rebased" in usage


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_keeps_every_non_body_line_of_the_record_and_rewrites_only_the_body_line_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_text().splitlines()
    ledger = repo / ".tdd/ledger.md"

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    new = record.read_text().splitlines()

    assert code == 0
    assert [line for line in new if not line.startswith("body: ")] == [
        line for line in old if not line.startswith("body: ")]
    assert [line for line in new if line.startswith("body: ")] != [
        line for line in old if line.startswith("body: ")]
    assert any(line.startswith("case: ") for line in old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_run_from_a_subdirectory_re_records_the_same_upstream_only_case_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"
    stale = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", "../.tdd/ledger.md", before], cwd=repo / "tests")
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    assert (stale, code, after) == (1, 0, 0)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_refuses_a_stale_case_the_branch_changed_since_its_record_and_names_it_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % (1, 1))
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % (5, 1))
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    suite.write_text(case % (9, 1))
    git(repo, "commit", "-q", "-a", "-m", "step two edits the frozen case")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text(case % (1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % earlier]


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_refuses_a_stale_case_the_branch_and_origin_both_edited_identically_since_its_record_because_its_pre_rebase_body_no_longer_matches_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % (1, 1))
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % (5, 1))
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    suite.write_text(case % (1, 3))
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-a", "-m", "step two edits the frozen case as origin will")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text(case % (1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % earlier]


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_refuses_a_stale_case_whose_head_body_differs_from_origins_though_the_record_matched_before_the_rebase_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % (1, 1))
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % (5, 1))
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / "lib.py").write_text("one\n")
    git(repo, "add", "lib.py")
    git(repo, "commit", "-q", "-m", "step two")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text(case % (1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % earlier]


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_1_naming_only_the_refused_case_while_re_recording_the_other_stale_one_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    case = "def test_%s_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suites = {name: repo / ("tests/test_%s.py" % name) for name in ("kept", "refused")}
    for name, suite in suites.items():
        suite.write_text(case % (name, 1, 1))
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    steps = {"kept": "step one pins the kept case", "refused": "step two pins the refused case"}
    current = "step three adds another"
    git(repo, "checkout", "-q", "-b", "work")
    for name, suite in suites.items():
        suite.write_text(case % (name, 5 if name == "refused" else 1, 2 if name == "kept" else 1))
        run_cli(tests_frozen, ["record", "--step", steps[name], "tests/test_%s.py" % name], cwd=repo)
        git(repo, "add", "tests")
        git(repo, "commit", "-q", "-m", "step " + name)
    suites["refused"].write_text(case % ("refused", 9, 1))
    git(repo, "commit", "-q", "-a", "-m", "step three edits the refused case")
    (repo / ".tdd/ledger.md").write_text(
        "- [x] %s\n- [x] %s\n- [ ] %s\n" % (steps["kept"], steps["refused"], current))

    git(repo, "checkout", "-q", "main")
    suites["kept"].write_text(case % ("kept", 1, 2))
    git(repo, "commit", "-q", "-a", "-m", "upstream 2")
    for name, suite in suites.items():
        suite.write_text(case % (name, 1, 3))
    git(repo, "commit", "-q", "-a", "-m", "upstream 3")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    records = sorted((repo / ".tdd").glob("tests-frozen-*.record"))
    old = {path: path.read_bytes() for path in records}

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    changed = [path for path in records if path.read_bytes() != old[path]]
    kept_check = run_cli(tests_frozen, ["check-earlier", str(repo / ".tdd/ledger.md"), "--step", current],
                         cwd=repo)[1]
    assert (code, len(changed)) == (1, 1)
    assert out.splitlines() == ["test_refused_2552 (%s)" % steps["refused"]]
    assert "test_kept_2552" not in kept_check


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_3_and_rewrites_no_record_when_no_earlier_recorded_case_is_stale_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code, out, record.read_bytes()) == (3, "", old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord a case two steps recorded")
def test_rerecord_rebased_exits_3_printing_nothing_for_a_case_whose_older_owners_superseded_record_is_stale_and_check_earlier_passes_3150(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_3150():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    older, later, current = "step one pins the config", "step two repins the config", "step three adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", older, "tests/test_suite.py"], cwd=repo)
    suite.write_text(case % 3)
    run_cli(tests_frozen, ["record", "--step", later, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "steps one and two")
    ledger = repo / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (older, later, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    earlier_code, earlier_out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)

    assert (code, out, earlier_code, earlier_out) == (3, "", 0, "")


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord a case two steps recorded")
def test_rerecord_rebased_exits_1_naming_the_latest_owning_step_and_not_the_older_one_when_the_branch_changed_the_body_3150(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_3150():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    older, later, current = "step one pins the config", "step two repins the config", "step three adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", older, "tests/test_suite.py"], cwd=repo)
    suite.write_text(case % 3)
    run_cli(tests_frozen, ["record", "--step", later, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "steps one and two")
    suite.write_text(case % 4)
    git(repo, "commit", "-q", "-a", "-m", "step three edits the case")
    ledger = repo / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (older, later, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)

    assert (code, out.splitlines()) == (1, ["test_config_3150 (%s)" % later])


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord a case two steps recorded")
def test_rerecord_rebased_re_records_the_latest_owners_record_and_leaves_the_older_steps_record_untouched_when_the_default_branch_changed_the_body_3150(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_3150():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    older, later, current = "step one pins the config", "step two repins the config", "step three adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", older, "tests/test_suite.py"], cwd=repo)
    (older_record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    suite.write_text(case % 3)
    run_cli(tests_frozen, ["record", "--step", later, "tests/test_suite.py"], cwd=repo)
    (later_record,) = set((repo / ".tdd").glob("tests-frozen-*.record")) - {older_record}
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "steps one and two")
    ledger = repo / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (older, later, current))

    git(repo, "checkout", "-q", "main")
    suite.write_text((case % 3).replace("a = 1", "a = 9"))
    git(repo, "commit", "-q", "-a", "-m", "upstream changes the body")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    older_bytes, later_bytes = older_record.read_bytes(), later_record.read_bytes()

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    earlier_code, _, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)

    assert (code, older_record.read_bytes() == older_bytes, later_record.read_bytes() != later_bytes,
            earlier_code) == (0, True, True, 0)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord with a missing ledger")
def test_rerecord_rebased_exits_2_naming_an_unreadable_ledger_on_stderr_and_writes_no_record_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    suite.write_text("def test_config_2552():\n    assert f() == 1\n")
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    run_cli(tests_frozen, ["record", "--step", "step one pins the config", "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    ledger = repo / ".tdd/unreadable-ledger.md"
    ledger.mkdir()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()

    code, out, err = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), head], cwd=repo)

    assert (code, out, record.read_bytes()) == (2, "", old)
    assert str(ledger) in err


@pytest.mark.process("a real git repository with an origin remote under tmp_path, asked to rerecord with no ledger file")
def test_rerecord_rebased_with_no_ledger_file_exits_3_with_no_output_and_rewrites_no_record_2718(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    (repo / "tests/test_suite.py").write_text("def test_config_2718():\n    assert f() == 1\n")
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    run_cli(tests_frozen, ["record", "--step", "step one pins the config", "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/no-ledger-yet.md"), head], cwd=repo)

    assert (code, out, record.read_bytes()) == (3, "", old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_2_and_rewrites_no_record_when_the_pre_rebase_sha_names_no_commit_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), "0" * 40], cwd=repo)

    assert (code, out, record.read_bytes()) == (2, "", old)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, an earlier record that cannot be read")
def test_rerecord_rebased_exits_2_naming_the_record_when_an_earlier_steps_record_exists_but_cannot_be_read_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    suite.write_text("def test_config_2552():\n    assert f() == 1\n")
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    earlier, current = "step one pins the config", "step two adds another"
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    record.unlink()
    record.mkdir()
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                          text=True).stdout.strip()

    code, out, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), head], cwd=repo)

    assert (code, out, record.name in err) == (2, "", True)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_skips_a_ticked_earlier_step_with_no_record_file_and_still_re_records_the_stale_one_2552(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    unrecorded, earlier, current = "step zero recorded nothing", "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (unrecorded, earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    assert (code, out, after) == (0, "", 0)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, the stale record's write made to raise")
def test_rerecord_rebased_exits_2_naming_the_record_when_writing_a_stale_cases_re_record_raises_2552(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(repo)

    code = tests_frozen.rerecord_rebased(str(repo / ".tdd/ledger.md"), before)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, the stale record's write made to raise")
def test_rerecord_rebased_exits_2_naming_the_record_when_writing_a_stale_cases_re_record_raises_file_not_found_so_it_is_not_read_as_a_missing_ledger_2718(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2552():\n    assert f() == %d\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise FileNotFoundError(2, "No such file or directory", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(repo)

    code = tests_frozen.rerecord_rebased(str(repo / ".tdd/ledger.md"), before)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


STEPS = ["step Z adds an early case", "step A adds the cases", "step B adds a later case"]
CASE = "def test_%s():\n    assert %d\n"


def _skip_lines(err, what):
    return sum(1 for l in err.splitlines() if l == "skipped: " + what or l.startswith("skipped: " + what + " ("))


def _ledger(repo, **state):
    """The ledger in its real shapes: open, pending (ticked, ledger.PENDING_MARK appended) and done."""
    marks = {"open": "- [ ] %s", "pending": "- [x] %s ⟂ refactor pending", "done": "- [x] %s"}
    (repo / ".tdd/issue-9.md").write_text("".join(
        marks[state.get(name, "open")] % text + "\n" for name, text in zip("ZAB", STEPS)))


def _commit(repo, message):
    git(repo, "commit", "-q", "-am", message)


def _plan_repo(repo, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "9")
    (repo / ".tdd").mkdir()
    (repo / "test_suite.py").write_text(CASE % ("base", 0))
    _ledger(repo)
    (repo / ".tdd/issue-8.md").write_text("- [x] %s\n" % STEPS[1])
    new_repo(repo)
    git(repo, "add", "test_suite.py", ".tdd/issue-9.md", ".tdd/issue-8.md")
    git(repo, "commit", "-q", "-m", "plan")


def _names(repo, tests_frozen, step):
    record = (repo / tests_frozen.record_path(step)).read_text()
    return sorted(l[6:] for l in record.splitlines() if l.startswith("case: "))


@pytest.mark.process("a real git repository under tmp_path, its history walked after an earlier case's receipt")
def test_rerecord_on_head_walks_the_real_ledger_history_after_an_earlier_case_left_a_receipt_and_first_imported_ledger_3053(
        tmp_path, run_cli, monkeypatch):
    for name in ("ledger", "veri.tests_frozen"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    (tmp_path / "earlier").mkdir()
    with pytest.MonkeyPatch.context() as earlier_case:
        receipt_leaver(earlier_case)(tmp_path / "earlier" / "ledger.md")
        tests_frozen = importlib.import_module("veri.tests_frozen")
    repo, step = tmp_path / "repo", STEPS[1]
    repo.mkdir()
    suite = repo / "test_suite.py"
    _plan_repo(repo, monkeypatch)
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("one", 1))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=repo)
    _commit(repo, "A red")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("pin_committed", 5))
    _commit(repo, "A pin, not ticked yet")

    code, _, err = run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=repo)

    assert (code, _names(repo, tests_frozen, step)) == (0, ["test_one", "test_pin_committed"]), err


BODY = "def test_%s():\n    x = %d\n    assert x\n"


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_case_the_verified_refactor_tidied_and_leaves_one_already_stale_at_green_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    suite.write_text(suite.read_text().replace("x = 2\n    assert x\n", "x = 3\n    assert x\n"))
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2], "--except", "test_two"],
                     cwd=tmp_path)[:2]
    refused = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, spared, refused) == (1, (0, ""), (1, "test_two (%s)\n" % step))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_body_the_refactor_moved_into_a_shared_helper_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    helper = "def _value(n):\n    return n\n\n\n"
    suite.write_text(helper + suite.read_text().replace("x = 1\n", "x = _value(1)\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_an_earlier_steps_case_whose_assertion_line_the_refactor_only_reformatted_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), "def test_one():\n    x = 1\n    assert x == 1\n"]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("assert x == 1\n", "assert x==1\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_python_cases_record_when_the_refactor_changed_an_assertion_line_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n    assert x\n", "x = 1\n    assert x > 5\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_javascript_cases_record_when_the_refactor_changed_an_expect_line_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.js"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("it('one', () => {\n  const x = 1;\n  expect(x).toBe(1);\n});\n")
    git(tmp_path, "add", "suite.test.js")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.js"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("expect(x).toBe(1)", "expect(x).toBeGreaterThan(5)"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("before, after", [
    ('t.Fatalf("got %d", x)', 't.Fatalf("got %d, want 5", x+1)'),
    ('t.Errorf("got %d", x)', 't.Errorf("got %d, want 5", x+1)'),
    ('t.Fail()', 't.FailNow()'),
    ('require.Equal(t, 1, x)', 'require.Equal(t, 5, x)'),
])
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_changed_its_check_line_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch, before, after):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\t%s\n\t}\n}\n" % before)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace(before, after))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestOne (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_after_the_last_case_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n'
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_a_check_into_a_helper_between_two_cases_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    two = 'func TestTwo(t *testing.T) {\n\tif 2 != 2 {\n\t\tt.Fatal("c")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n'
              + two)
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n}\n\n' + two)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_go_case_whose_refactor_moved_checks_into_a_new_helper_while_it_also_calls_an_asserting_helper_green_had_3077(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    build = 'func build(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatalf("build failed")\n\t}\n}\n'
    inline = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build)
    extracted = ('func TestOne(t *testing.T) {\n\tbuild(t)\n\tx := 1\n\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
                 '\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n}\n\n' + build)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (rerecorded, checked) == ((0, "", ""), (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_two_go_cases_whose_refactor_moved_the_same_checks_verbatim_into_one_new_shared_helper_3332(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    checks = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
    inline = ''.join('func %s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks) for n in ("TestOne", "TestTwo"))
    extracted = (''.join('func %s(t *testing.T) {\n\tx := 1\n\tcheckShort(t, x)\n}\n\n' % n for n in ("TestOne", "TestTwo"))
                 + 'func checkShort(t *testing.T, x int) {\n%s}\n' % checks)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    rerecorded = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (rerecorded, checked) == ((0, "", ""), (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_two_go_cases_whose_refactor_moved_the_checks_into_one_new_shared_helper_but_changed_one_3332(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    checks = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
    changed = checks.replace('t.Fatal("b")', 't.Fatal("c")')
    inline = ''.join('func %s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks) for n in ("TestOne", "TestTwo"))
    extracted = (''.join('func %s(t *testing.T) {\n\tx := 1\n\tcheckShort(t, x)\n}\n\n' % n for n in ("TestOne", "TestTwo"))
                 + 'func checkShort(t *testing.T, x int) {\n%s}\n' % changed)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    recorded = (tmp_path / ".tdd/issue-9.md").read_text()

    _, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (_skip_lines(err, "suite_test.go TestOne"), _skip_lines(err, "suite_test.go TestTwo"),
            (tmp_path / ".tdd/issue-9.md").read_text() == recorded) == (1, 1, True), err


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_the_record_and_check_earlier_exits_1_for_a_go_case_whose_refactor_moved_checks_into_a_helper_after_it_and_dropped_one_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + chk("c") + '}\n'
    dropped = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
               'func check(t *testing.T, x int) {\n' + chk("a") + '}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(dropped)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, checked) == (1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_prints_one_stderr_line_naming_each_case_it_left_unrecorded_and_still_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + '}\n'
    dropped = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '}\n'
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(dropped)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (code, _skip_lines(err, "suite_test.go TestOne")) == (1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_a_case_gone_at_head_a_digest_mismatch_and_an_assertionless_shape_change_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = '\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n'
    fn = lambda name, body: 'func %s(t *testing.T) {\n%s}\n\n' % (name, body)
    suite.write_text(fn("TestGone", "\tx := 1\n" + chk) + fn("TestMismatch", "\tx := 1\n" + chk) + fn("TestBare", "\tx := 1\n"))
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    suite.write_text(fn("TestGone", "\tx := 1\n" + chk) + fn("TestMismatch", "\tx := 1\n\ty := 2\n" + chk) + fn("TestBare", "\tx := 1\n"))
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(fn("TestMismatch", "\tx := 1\n\ty := 2\n" + chk) + fn("TestBare", "\tx := 2\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (code, sorted(l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped:"))) == (1, [
        "skipped: suite_test.go TestBare", "skipped: suite_test.go TestGone", "skipped: suite_test.go TestMismatch"])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_heals_a_format_2_go_record_cut_with_the_body_running_past_the_closing_brace_so_check_earlier_exits_0_2863(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    import hashlib
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m
    other = '\nfunc other(t *testing.T) {\n\tt.Fatal("z")\n}\n'
    inline = 'func TestOne(t *testing.T) {\n\tx := 1\n' + chk("a") + chk("b") + '}\n' + other
    extracted = ('func TestOne(t *testing.T) {\n\tx := 1\n' + chk("b") + '\tcheck(t, x)\n}\n\n'
                 'func check(t *testing.T, x int) {\n' + chk("a") + '}\n' + other)
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    record = tmp_path / run_cli(tests_frozen, ["path", step], cwd=tmp_path)[1].strip()
    old_digest = hashlib.sha256(inline.rstrip().encode()).hexdigest()
    record.write_text("".join(
        "body: suite_test.go\tTestOne\t%s\n" % old_digest if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, checked) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_the_record_of_a_case_with_no_assertion_line_when_the_refactor_changed_its_body_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestOne(t *testing.T) {\n\tx := 1\n\tpanic(x)\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("panic(x)", "panic(x + 1)"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestOne (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_cases_record_when_the_refactor_changed_its_title_and_body_together_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("def test_one():\n    x = 1\n", "def test_uno():\n    x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "test_one (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_still_re_records_the_other_cases_when_the_refactor_renamed_one_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("def test_one():\n", "def test_uno():\n")
                     .replace("x = 2\n", "x = 3 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2], "--except", "test_one"],
                     cwd=tmp_path)[:2]

    assert (code, spared) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_still_re_records_the_other_cases_when_an_earlier_refactor_renamed_one_before_green_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", STEPS[1], "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    suite.write_text(suite.read_text().replace("def test_one():\n", "def test_uno():\n"))
    _commit(tmp_path, "A refactor renames a case")
    _ledger(tmp_path, A="done", B="pending")
    suite.write_text(suite.read_text() + "\n\n" + CASE % ("later", 9))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 2\n", "x = 3 - 1\n"))
    _commit(tmp_path, "B refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    spared = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C", "--except", "test_one"],
                     cwd=tmp_path)[:2]

    assert (code, spared) == (0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_nothing_and_exits_3_unless_verdict_refactor_exit_holds_0_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    verdict, ledger = tmp_path / ".tdd/verdict-refactor.exit", ".tdd/issue-9.md"

    def records():
        return {str(p): p.read_bytes() for p in sorted((tmp_path / ".tdd").rglob("*"))
                if p.is_file() and p != verdict}
    before, outcomes = records(), []
    for held in (None, "1"):
        if held is not None:
            verdict.write_text(held)
        outcomes.append((run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0],
                         records() == before))

    assert outcomes == [(3, True), (3, True)]


@pytest.mark.process("git asked for the repository toplevel from a directory under tmp_path that is in none")
def test_rerecord_refactored_run_outside_any_git_repository_exits_2_and_re_records_nothing_2626(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    ledger, record = tmp_path / ".tdd/issue-9.md", tmp_path / ".tdd/record"
    ledger.write_text("- [x] step one\n")
    record.write_text("kept\n")

    code, out, _ = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", "deadbeef"], cwd=tmp_path)

    assert (code, out, record.read_text()) == (2, "", "kept\n")


@pytest.mark.process("git asked for the repository toplevel from a repository under tmp_path")
def test_rerecord_refactored_unreadable_ledger_exits_2_and_re_records_nothing_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    _plan_repo(tmp_path, monkeypatch)
    (tmp_path / ".tdd/issue-9.md").unlink(missing_ok=True)
    (tmp_path / ".tdd/issue-9.md").mkdir()
    record = tmp_path / ".tdd/record"
    record.write_text("kept\n")

    code, out, _ = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", "deadbeef"], cwd=tmp_path)

    assert (code, out, record.read_text()) == (2, "", "kept\n")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_exits_2_naming_the_record_when_writing_it_raises_2626(
        tmp_path, run_cli, tests_frozen, monkeypatch, capfd):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(tmp_path)

    code = tests_frozen.rerecord_refactored(".tdd/issue-9.md", green)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_case_with_no_assertion_line_when_the_refactor_only_changed_whitespace_2809(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), "def test_one():\n    x = 1\n    check(x)\n"]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("check(x)\n", "check( x )\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_a_go_case_on_a_skipped_line_and_check_earlier_exits_1_when_a_refactor_moved_its_assertions_into_assert_refused_and_dropped_one_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif v != "x" {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tv := "x"\n' + chk("a") + chk("b") + '}\n'
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, v)\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(moved)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "suite_test.go TestOne"), checked) == (1, 1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_a_go_case_on_a_skipped_line_and_check_earlier_exits_1_when_a_refactor_moved_its_assertions_into_assert_refused_and_deleted_the_call_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif v != "x" {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tv := "x"\n' + chk("a") + chk("b") + '}\n'
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\t_ = v\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(moved)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "suite_test.go TestOne"), checked) == (1, 1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_exits_3_and_check_earlier_exits_1_when_a_refactor_moved_a_go_cases_assertions_into_assert_refused_and_the_verdict_is_not_0_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif v != "x" {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tv := "x"\n' + chk("a") + chk("b") + '}\n'
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, v)\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(moved)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("1")
    ledger = ".tdd/issue-9.md"

    code = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[0]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, checked) == (3, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_without_a_skipped_line_and_check_earlier_exits_0_when_a_refactor_moved_its_assertions_into_assert_refused_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif v != "x" {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tv := "x"\n' + chk("a") + chk("b") + '}\n'
    moved = ('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n'
             'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, "x")\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(moved)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "suite_test.go TestOne"), checked) == (0, 0, 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_check_earlier_at_exit_1_when_an_assertion_is_deleted_from_assert_refused_after_a_successful_re_record_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    chk = lambda m: '\tif v != "x" {\n\t\tt.Fatal("%s")\n\t}\n' % m
    inline = 'func TestOne(t *testing.T) {\n\tv := "x"\n' + chk("a") + chk("b") + '}\n'
    case = 'func TestOne(t *testing.T) {\n\tv := "x"\n\tassertRefused(t, "x")\n}\n'
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text('func assertRefused(t *testing.T, v string) {\n' + chk("a") + chk("b") + '}\n\n' + case)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    first = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    suite.write_text('func assertRefused(t *testing.T, v string) {\n' + chk("a") + '}\n\n' + case)
    _commit(tmp_path, "A refactor drops an assertion from the helper")

    second = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (first[0], _skip_lines(first[2], "suite_test.go TestOne"), second[0], checked) == (
        0, 0, 1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_python_case_without_a_skipped_line_and_check_earlier_exits_0_when_a_refactor_moved_its_assert_into_assert_refused_2898(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("class TestSuite:\n    def test_one(self):\n        x = 1\n        assert x == 1\n")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("class TestSuite:\n    def test_one(self):\n        x = 1\n        assert_refused(x)\n\n\ndef assert_refused(x):\n    assert x == 1\n")
    _commit(tmp_path, "A refactor moves the assert into assert_refused")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 0, 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_its_t_fatal_line_without_moving_it_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t}\n}\n")
    _commit(tmp_path, "A refactor drops the check")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_t_fatal_lines_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_its_t_fatal_lines_moved_into_another_test_function_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestShared(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tTestShared(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the check into another test")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_python_case_whose_assert_line_a_refactor_moved_into_a_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_suite.py"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("def test_one():\n    x = 1\n    assert x == 1\n")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("def check_one(x):\n    assert x == 1\n\n\ndef test_one():\n    x = 1\n    check_one(x)\n")
    _commit(tmp_path, "A refactor moves the assert into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_a_later_commit_deleted_a_t_fatal_line_from_the_helper_it_calls_2837(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n\nfunc TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the checks into a helper")
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    _commit(tmp_path, "A refactor drops a check from the helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_go_cases_record_when_the_refactor_deleted_one_of_two_identical_t_fatal_lines_while_moving_the_other_into_a_helper_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"bad\")\n\tt.Error(\"mid\")\n\tt.Fatal(\"bad\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T) {\n\tt.Fatal(\"bad\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t)\n\tt.Error(\"mid\")\n}\n")
    _commit(tmp_path, "A refactor moves one check into a helper and drops the other")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (1, "TestX (%s)\n" % step)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_setup_t_fatal_lines_a_refactor_moved_into_a_helper_ahead_of_later_assertions_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_whose_helper_lines_sort_before_its_own_remaining_assertion_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n\tt.Fatal(\"z later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"a setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tsetupX(t)\n\tt.Fatal(\"z later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_run_again_with_the_same_green_sha_heals_an_order_changing_helper_extractions_stale_record_2853(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tt.Fatal(\"setup\")\n\tt.Error(\"later\")\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func setupX(t *testing.T) {\n\tt.Fatal(\"setup\")\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tsetupX(t)\n\tt.Error(\"later\")\n}\n")
    _commit(tmp_path, "A refactor extracts the setup check into a helper")
    ledger = ".tdd/issue-9.md"
    verdict = tmp_path / ".tdd/verdict-refactor.exit"
    verdict.write_text("1")
    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    verdict.write_text("0")

    run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert checked == (0, "")


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_exits_2_naming_the_record_and_the_title_when_an_earlier_steps_recorded_case_is_missing_at_head_2825(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    suite.write_text("def test_other_2825():\n    assert f() == 0\n")
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    earlier, current = "step one pins the config", "step two adds another"
    suite.write_text("def test_other_2825():\n    assert f() == 0\n\n\ndef test_config_before_rename_2825():\n    assert f() == 1\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    git(repo, "commit", "-q", "-a", "-m", "step one")
    pre = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                         text=True).stdout.strip()
    suite.write_text("def test_other_2825():\n    assert f() == 0\n\n\ndef test_config_after_rename_2825():\n    assert f() == 1\n")
    git(repo, "commit", "-q", "-a", "-m", "rename")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    code, _, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), pre], cwd=repo)

    assert (code, record.name in err, "test_config_before_rename_2825" in err, "KeyError" in err) == (
        2, True, True, False)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_whose_body_record_digest_is_neither_greens_nor_heads_and_leaves_its_record_untouched_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    record.write_text("".join(
        "body: suite_test.go\tTestX\t%s\n" % ("f" * 64) if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x := 1", "x := 1 // one"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, 1, 1, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_refactor_lost_a_helper_assertion_line_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n"
                     "\tif x < 0 {\n\t\tt.Error(\"negative\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("\tif x < 0 {\n\t\tt.Error(\"negative\")\n\t}\n", ""))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (tests_frozen.body_line("suite_test.go", "TestX", head_body).encode() + b"\n" in before,
            b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, True, 1, 1, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_refreshes_the_helpers_line_of_a_go_case_already_recorded_at_heads_body_so_check_earlier_exits_0_2973(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    green_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    suite.write_text(suite.read_text().replace("x := 1", "x := 1 // one").replace('"bad"', '"bad value"'))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    record.write_text(record.read_text().replace(
        tests_frozen.body_line("suite_test.go", "TestX", green_body),
        tests_frozen.body_line("suite_test.go", "TestX", head_body)))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "suite_test.go TestX") > 0,
            "helpers: suite_test.go\tTestX\t%s\n" % held in record.read_text(), checked) == (
        0, False, True, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    green_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    older = "helpers: suite_test.go\tTestX\t%s\n" % ("6" * 64)
    record.write_text("".join(
        tests_frozen.body_line("suite_test.go", "TestX", head_body) + "\n"
        if line.startswith("body: ") else older if line.startswith("helpers: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "suite_test.go TestX") > 0,
            "helpers: suite_test.go\tTestX\t%s\n" % held in record.read_text(), checked) == (
        0, False, True, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_when_the_refactor_lost_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    kept = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireTwo(t *testing.T, x int) {\n" + kept + "}\n\n"
                     "func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireTwo(t, x)\n}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into helpers; TestX's loses one")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    heads = {case: tests_frozen._bodies_of(suite.read_text(), case)[0] for case in ("TestX", "TestY")}
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\t%s\t%s\n" % (tests_frozen.body_line(
            "suite_test.go", line.split("\t")[1], heads[line.split("\t")[1]]), line.split("\t")[1], "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    x_lines = [line for line in record.read_text().splitlines() if "\tTestX\t" in line]
    held = "helpers: suite_test.go\tTestY\t%s" % tests_frozen._helper_digest(suite.read_text(), heads["TestY"])

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    after = record.read_text().splitlines()

    assert (code, _skip_lines(err, "suite_test.go TestX"),
            _skip_lines(err, "suite_test.go TestY"),
            [line for line in after if "\tTestX\t" in line] == x_lines, held in after) == (
        1, 1, 0, True, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_at_heads_body_whose_helpers_digest_is_neither_greens_nor_heads_when_the_refactor_added_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    kept = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + kept + "}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n\n"
                     "func TestY(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper; TestX's gains one")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    heads = {case: tests_frozen._bodies_of(suite.read_text(), case)[0] for case in ("TestX", "TestY")}
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\t%s\t%s\n" % (tests_frozen.body_line(
            "suite_test.go", line.split("\t")[1], heads[line.split("\t")[1]]), line.split("\t")[1], "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    x_lines = [line for line in record.read_text().splitlines() if "\tTestX\t" in line]
    held = "helpers: suite_test.go\tTestY\t%s" % tests_frozen._helper_digest(suite.read_text(), heads["TestY"])

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    after = record.read_text().splitlines()

    assert (code, _skip_lines(err, "suite_test.go TestX"),
            _skip_lines(err, "suite_test.go TestY"),
            [line for line in after if "\tTestX\t" in line] == x_lines, held in after) == (
        1, 1, 0, True, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_a_go_case_whose_body_digest_is_neither_greens_nor_heads_while_its_helpers_digest_is_greens_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n\tif x > 1 {\n\t\tt.Fatal(\"big\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    record.write_text("".join(
        "body: suite_test.go\tTestX\t%s\n" % ("f" * 64) if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % tests_frozen._helper_digest(
            suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0]))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x := 1", "x := 1 // one"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (b"\nhelpers: " in before, code, _skip_lines(err, "suite_test.go TestX"),
            record.read_bytes() == before) == (True, 1, 1, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_body_digest_guard_in_parentheses_on_the_skipped_line_of_a_case_whose_body_digest_is_neither_greens_nor_heads_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    record.write_text("".join(
        "body: suite_test.go\tTestX\t%s\n" % ("f" * 64) if line.startswith("body: ") else line
        for line in record.read_text().splitlines(keepends=True)))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x := 1", "x := 1 // one"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_helpers_digest_guard_in_parentheses_on_the_skipped_line_of_a_record_at_greens_body_whose_helpers_digest_differs_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    with record.open("a") as handle:
        handle.write("helpers: suite_test.go\tTestX\t%s\n" % ("0" * 64))
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text() + "\n// tidied\n")
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_assertion_lines_guard_in_parentheses_on_the_skipped_line_of_a_head_body_record_whose_case_and_helpers_lost_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    kept = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireTwo(t *testing.T, x int) {\n" + kept + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireTwo(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper and loses one")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    record.write_text("".join(
        "%s\nhelpers: suite_test.go\tTestX\t%s\n" % (tests_frozen.body_line("suite_test.go", "TestX", head), "6" * 64)
        if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_helper_assertion_count_guard_in_parentheses_on_the_skipped_line_of_a_record_whose_case_body_is_unchanged_but_whose_helper_gained_an_assertion_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    one = "\tif x != 1 {\n\t\tt.Fatal(\"bad 1\")\n\t}\n"
    two = one + "\tif x != 2 {\n\t\tt.Fatal(\"bad 2\")\n\t}\n"
    case = "func TestX(t *testing.T) {\n\tx := 1\n\tcheckX(t, x)\n}\n"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func checkX(t *testing.T, x int) {\n" + one + "}\n\n" + case)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func checkX(t *testing.T, x int) {\n" + two + "}\n\n" + case)
    _commit(tmp_path, "A refactor adds an assertion to the helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        0, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_names_the_assertionless_shape_guard_in_parentheses_on_the_skipped_line_of_a_case_with_no_assertion_lines_whose_body_changed_2985(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestX(t *testing.T) {\n\tx := 2\n}\n")
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    lines = [l for l in err.splitlines() if l.startswith("skipped: suite_test.go TestX")]
    assert (code, len(lines), [l.startswith("skipped: suite_test.go TestX (") and l.endswith(")")
                               and len(l) > len("skipped: suite_test.go TestX ()") for l in lines]) == (
        1, 1, [True])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_one_helpers_line_from_head_for_a_go_case_whose_record_held_two_stale_ones_so_check_earlier_exits_0_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    head_body = tests_frozen._bodies_of(suite.read_text(), "TestX")[0]
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line for line in record.read_text().splitlines(keepends=True) if not line.startswith("body: ")
    ).replace("case: TestX\n", "case: TestX\n" + tests_frozen.body_line("suite_test.go", "TestX", head_body)
              + "\n" + stale))
    held = tests_frozen._helper_digest(suite.read_text(), head_body)

    run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ".tdd/issue-9.md", "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert ([l for l in record.read_text().splitlines() if l.startswith("helpers: ")], checked) == (
        ["helpers: suite_test.go\tTestX\t%s" % held], (0, ""))


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_leaves_one_helpers_line_from_head_for_a_go_case_whose_record_held_two_stale_ones_so_check_earlier_exits_0_2998(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    new_repo(tmp_path)
    (tmp_path / "base.txt").write_text("base\n")
    git(tmp_path, "add", "base.txt")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line + stale if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    git(tmp_path, "add", "suite_test.go")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", "-f", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    git(tmp_path, "add", "suite_test.go")
    git(tmp_path, "commit", "-q", "-m", "edit moves the assertions into a helper")
    held = tests_frozen._helper_digest(suite.read_text(), tests_frozen._bodies_of(suite.read_text(), "TestX")[0])

    run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)[:2]

    assert ([l for l in record.read_text().splitlines() if l.startswith("helpers: ")], checked) == (
        ["helpers: suite_test.go\tTestX\t%s" % held], (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_leaves_a_record_with_two_helpers_lines_byte_identical_for_a_case_it_skips_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func TestX(t *testing.T) {\n\tx := 2\n}\n")
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    stale = "".join("helpers: suite_test.go\tTestX\t%s\n" % (digit * 64) for digit in "67")
    record.write_text("".join(
        line + stale if line.startswith("body: ") else line for line in record.read_text().splitlines(keepends=True)))
    before = record.read_bytes()

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert (code, "skipped: suite_test.go TestX" in err, record.read_bytes()) == (1, True, before)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_keeps_a_helpers_line_of_a_later_case_that_does_not_follow_a_rewritten_body_2998(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    asserts = "".join("\tif x != %d {\n\t\tt.Fatal(\"bad %d\")\n\t}\n" % (n, n) for n in (1, 2, 3))
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("func TestX(t *testing.T) {\n\tx := 1\n" + asserts + "}\n")
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text("func requireAll(t *testing.T, x int) {\n" + asserts + "}\n\n"
                     "func TestX(t *testing.T) {\n\tx := 1\n\trequireAll(t, x)\n}\n")
    _commit(tmp_path, "A refactor moves the assertions into a helper")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    later = "case: TestY\nhelpers: suite_test.go\tTestY\t%s\n" % ("8" * 64)
    record.write_text(record.read_text() + later)

    run_cli(tests_frozen, ["rerecord-refactored", ".tdd/issue-9.md", green], cwd=tmp_path)

    assert record.read_text().endswith(later)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_drops_a_recorded_case_never_committed_on_the_branch_instead_of_exiting_2_2994(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    kept = "def test_kept_2994():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == 1\n"
    ghost = "\n\ndef test_ghost_2994():\n    assert f() == 2\n"
    suite.write_text("")
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the kept case", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(kept + ghost)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    suite.write_text(kept)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code in (0, 3), "test_ghost_2994" in record.read_text()) == (True, False)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_drops_the_helpers_line_of_a_recorded_go_case_never_committed_on_the_branch_2994(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/suite_test.go"
    kept = "func TestKept(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
    ghost = "\nfunc TestGhost(t *testing.T) {\n\tx := 2\n\tif x != 2 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
    suite.write_text("")
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the kept case", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(kept + ghost)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/suite_test.go"], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    lines = record.read_text().splitlines(keepends=True)
    at = next(i for i, l in enumerate(lines) if l.startswith("case: TestGhost")) + 1
    record.write_text("".join(lines[:at + 1] + ["helpers: tests/suite_test.go\tTestGhost\t%s\n" % ("a" * 64)]
                              + lines[at + 1:]))
    suite.write_text(kept)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), before], cwd=repo)

    assert (code in (0, 3), "TestGhost" in record.read_text(), "a" * 64 in record.read_text()) == (
        True, False, False)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_drops_only_the_never_committed_case_and_still_re_records_the_upstream_only_changed_one_2994(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    case = "def test_config_2994():\n    assert f() == %d\n"
    ghost = "\n\ndef test_ghost_2994():\n    assert f() == 9\n"
    suite.write_text(case % 1)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the config", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(case % 2 + ghost)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    suite.write_text(case % 2)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "step one")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    for value in (2, 3):
        suite.write_text(case % value)
        git(repo, "commit", "-q", "-a", "-m", "upstream %d" % value)
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                            text=True).stdout.strip()
    git(repo, "rebase", "-q", "origin/main")
    ledger = repo / ".tdd/ledger.md"
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", current], cwd=repo)[0]

    text = record.read_text()
    assert (code, "test_config_2994" in text, "test_ghost_2994" in text, after) == (0, True, False, 0)


@pytest.mark.process("a real git repository with an origin remote under tmp_path, rebased onto its default branch")
def test_rerecord_rebased_still_exits_2_for_a_recorded_case_committed_at_the_pre_rebase_sha_and_gone_at_head_2994(
        tmp_path, run_cli, tests_frozen):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / ".tdd").mkdir()
    suite = repo / "tests/test_suite.py"
    kept = "def test_kept_2994():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == 1\n"
    ghost = "\n\ndef test_ghost_2994():\n    assert f() == 2\n"
    suite.write_text(kept)
    new_repo(repo)
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    git(tmp_path, "clone", "-q", "--bare", str(repo), "origin.git")
    git(repo, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")

    earlier, current = "step one pins the kept case", "step two adds another"
    git(repo, "checkout", "-q", "-b", "work")
    suite.write_text(kept + ghost)
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=repo)
    git(repo, "commit", "-q", "-a", "-m", "step one adds the ghost")
    with_ghost = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True,
                                text=True).stdout.strip()
    suite.write_text(kept)
    git(repo, "commit", "-q", "-a", "-m", "a later commit removes the ghost")
    (repo / ".tdd/ledger.md").write_text("- [x] %s\n- [ ] %s\n" % (earlier, current))

    git(repo, "checkout", "-q", "main")
    (repo / "README.md").write_text("upstream\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "upstream")
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "work")
    git(repo, "rebase", "-q", "origin/main")

    code, _, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/ledger.md"), with_ghost], cwd=repo)

    assert (code, "names case test_ghost_2994, which tests/test_suite.py does not hold at HEAD" in err) == (2, True)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_go_cases_sharing_a_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)
    checks = "".join('\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m for m in "abc")
    inline = "".join('func Test%s(t *testing.T) {\n\tx := 1\n%s}\n\n' % (n, checks)
                     for n in ("One", "Two", "Three"))
    shared = "".join('func Test%s(t *testing.T) {\n\tx := 1\n\tsharedBase(t, x)\n}\n\n' % n for n in ("One", "Two", "Three"))
    helper = ('func sharedBase(t *testing.T, x int) {\n\tif x != 1 {\n\t\tt.Fatal("a")\n\t}\n\tif x != 1 {\n\t\tt.Fatal("b")\n\t}\n'
              '\tif x != 1 {\n\t\tt.Fatal("c")\n\t}\n}\n')
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_a_function_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
    suite.write_text(inline)
    git(tmp_path, "add", "suite.test.ts")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.ts"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_a_function_helper_named_test_helper_the_refactor_introduced_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = "".join("it('%s', () => {\n  const x = 1;\n  testHelper();\n});\n\n" % n for n in names)
    helper = "function testHelper() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
    suite.write_text(inline)
    git(tmp_path, "add", "suite.test.ts")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.ts"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_printing_no_skipped_for_three_typescript_cases_sharing_an_arrow_function_helper_the_refactor_introduced_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    helper = "const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"
    suite.write_text(inline)
    git(tmp_path, "add", "suite.test.ts")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.ts"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, err, checked) == (0, "", (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_1_naming_the_cases_when_the_refactor_adds_an_assertion_line_to_the_shared_typescript_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(%d);\n});\n\n" % (n, i)
                     for i, n in enumerate(names, 1))
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n  expect(x).toBe(4);\n}\n"
    suite.write_text(inline)
    git(tmp_path, "add", "suite.test.ts")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.ts"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[2]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    skipped = [line for line in err.splitlines() if line.startswith("skipped: suite.test.ts ")]
    assert (bool(skipped), checked) == (True, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_only_the_go_case_whose_own_lines_the_shared_helper_exceeds_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "suite_test.go"
    _plan_repo(tmp_path, monkeypatch)

    def check(m):
        return '\tif x != 1 {\n\t\tt.Fatal("%s")\n\t}\n' % m

    inline = ("func TestX(t *testing.T) {\n\tx := 1\n" + check("a") + check("b") + "}\n\n"
              "func TestY(t *testing.T) {\n\tx := 1\n" + check("a") + check("b") + check("c") + "}\n\n")
    shared = "".join("func Test%s(t *testing.T) {\n\tx := 1\n\tsharedBase(t, x)\n}\n\n" % n for n in ("X", "Y"))
    helper = "func sharedBase(t *testing.T, x int) {\n" + check("a") + check("b") + check("c") + "}\n"
    suite.write_text(inline)
    git(tmp_path, "add", "suite_test.go")
    run_cli(tests_frozen, ["record", "--step", step, "suite_test.go"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[2]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    skipped = [l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped: ")]
    assert (skipped, checked) == (["skipped: suite_test.go TestX"], 1)


def _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper, shared=None):
    """Three TS cases with inline expects, refactored into `shared` + `helper`; returns (skipped lines, check-earlier code)."""
    step = STEPS[1]
    suite = tmp_path / "suite.test.ts"
    _plan_repo(tmp_path, monkeypatch)
    names = ("one", "two", "three")
    inline = "".join("it('%s', () => {\n  const x = 1;\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n});\n\n" % n
                     for n in names)
    shared = shared or "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n});\n\n" % n for n in names)
    suite.write_text(inline)
    git(tmp_path, "add", "suite.test.ts")
    run_cli(tests_frozen, ["record", "--step", step, "suite.test.ts"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(shared + helper)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"
    err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)[2]
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]
    return [l.split(" (")[0] for l in err.splitlines() if l.startswith("skipped: ")], checked


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("opener", ["let sharedBase = () => {", "return sharedBase = () => {"])
def test_rerecord_refactored_does_not_take_a_let_or_return_line_for_a_typescript_helper_definition_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, opener):
    helper = opener + "\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (len(skipped), checked) == (3, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_count_the_assertions_of_a_function_following_the_shared_typescript_helper_as_the_helpers_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "function unrelated() {\n  expect(x).toBe(9);\n}\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_every_case_and_check_earlier_exits_1_when_the_refactor_deletes_an_assertion_from_the_shared_typescript_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n}\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (len(skipped), checked) == (3, 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_skips_only_the_case_whose_helper_call_line_the_refactor_deleted_and_check_earlier_exits_1_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
    shared = "".join("it('%s', () => {\n  const x = 1;\n%s});\n\n" % (n, "  sharedBase();\n" if n != "two" else "")
                     for n in ("one", "two", "three"))

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper, shared)

    assert (skipped, checked) == (["skipped: suite.test.ts two"], 1)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_let_a_non_arrow_const_before_the_shared_typescript_arrow_helper_swallow_it_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("const y = 2;\n"
              "const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_count_the_assertions_of_a_non_arrow_const_following_the_shared_typescript_helper_as_the_helpers_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"
              "const unrelated = 3;\nexpect(x).toBe(9);\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_take_a_non_arrow_const_the_cases_call_for_a_typescript_helper_definition_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "const other = wrap(() => {\n  expect(x).toBe(9);\n});\n")
    shared = "".join("it('%s', () => {\n  const x = 1;\n  sharedBase();\n  other();\n});\n\n" % n
                     for n in ("one", "two", "three"))

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper, shared)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("opener", ["const sharedBase = async () => {", "const sharedBase = x => {"])
def test_rerecord_refactored_takes_an_async_or_single_parameter_typescript_arrow_const_for_the_shared_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, opener):
    helper = opener + "\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n};\n"

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
@pytest.mark.parametrize("word", ["constants", "functional"])
def test_rerecord_refactored_does_not_end_the_shared_typescript_helper_at_a_column_0_line_merely_starting_with_a_keyword_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch, word):
    helper = ("const sharedBase = () => {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n%s\n  expect(x).toBe(3);\n};\n" % word)

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_does_not_take_a_typescript_arrow_const_the_cases_do_not_call_for_their_helper_2942(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    helper = ("function sharedBase() {\n  expect(x).toBe(1);\n  expect(x).toBe(2);\n  expect(x).toBe(3);\n}\n"
              "const other = () => {\n  expect(x).toBe(9);\n};\n")

    skipped, checked = _ts_shared_move(tmp_path, run_cli, tests_frozen, monkeypatch, helper)

    assert (skipped, checked) == ([], 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_then_check_earlier_exits_0_for_a_python_case_whose_refactor_moved_assertions_into_a_module_level_helper_before_a_second_case_2931(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    suite = tmp_path / "test_sample.py"
    _plan_repo(tmp_path, monkeypatch)
    test_b = 'def test_b():\n    y = 2\n    assert y == 2\n    assert y != 3\n'
    inline = ('def test_a():\n    x = 1\n    assert x == 1\n    assert x != 2\n\n\n' + test_b)
    extracted = ('def assert_refused(x):\n    assert x == 1\n    assert x != 2\n\n\n'
                 'def test_a():\n    x = 1\n    assert_refused(x)\n\n\n' + test_b)
    suite.write_text(inline)
    git(tmp_path, "add", "test_sample.py")
    run_cli(tests_frozen, ["record", "--step", step, "test_sample.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(extracted)
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, "skipped:" in err, checked) == (0, False, (0, ""))


TWO_ASSERTS = "def test_%s():\n    x = %d\n    assert x\n    assert x > 0\n"


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_exits_0_having_skipped_a_case_whose_record_is_already_at_heads_body_3051(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), TWO_ASSERTS % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("    assert x > 0\n", ""))
    _commit(tmp_path, "A refactor")
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 1, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_exits_1_naming_a_case_whose_assertion_line_the_refactor_removed_and_check_earlier_still_refuses_3051(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), TWO_ASSERTS % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("    assert x > 0\n", ""))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    ledger = ".tdd/issue-9.md"

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", STEPS[2]], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (1, 1, 1), err


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_exits_2_not_1_when_check_earlier_cannot_obtain_an_answer_after_the_re_record_3051(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    _ledger(tmp_path, A="done")
    _commit(tmp_path, "A green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "A refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    monkeypatch.setattr(tests_frozen, "_check_earlier", lambda ledger, step, exempt=(), sanctioned=(): 2)
    monkeypatch.chdir(tmp_path)

    assert tests_frozen.rerecord_refactored(".tdd/issue-9.md", green) == 2


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_rewrites_body_and_helpers_lines_together_from_head_when_a_diff_checked_step_makes_a_case_call_a_new_helper_3052(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef check_old(x):\n    assert x == 1\n\n\n"
                     "def test_pinned_3052():\n    check_old(1)\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", "-f", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef check_new(x):\n    assert x == 1\n    assert x < 2\n\n\n"
                     "def test_pinned_3052():\n    check_new(1)\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit makes the case call a new helper")
    text = suite.read_text()
    head = tests_frozen._helper_digest(text, tests_frozen._bodies_of(text, "test_pinned_3052")[0])

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    held = [l.split("\t")[-1] for l in record.read_text().splitlines() if l.startswith("helpers: ")]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (rerecorded, held, code, out) == (0, [head], 0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_rerecord_earlier_leaves_no_helpers_line_for_a_case_that_calls_no_helper_at_head_3052(
        tmp_path, run_cli, tests_frozen):
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    new_repo(tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef check_old(x):\n    assert x == 1\n\n\n"
                     "def test_pinned_3052():\n    check_old(1)\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", "-f", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_pinned_3052():\n    assert 1 == 1\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit makes the case call no helper")

    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    (record,) = (tmp_path / ".tdd").glob("tests-frozen-*.record")
    held = [l for l in record.read_text().splitlines() if l.startswith("helpers: ")]

    assert (rerecorded, held) == (0, [])


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_re_records_a_case_a_later_suite_repair_green_rewrote_with_the_same_assertion_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / ledger).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_suite_repair_guard_skips_a_ledgers_header_and_blank_lines_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / ledger).write_text(
        "# Plan\n\n- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    checked = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[:2]

    assert (code, _skip_lines(err, "test_suite.py test_one"), checked) == (0, 0, (0, ""))


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_still_refuses_a_case_an_ordinary_green_rewrote_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    (tmp_path / ledger).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, STEPS[2]))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_refuses_a_case_an_ordinary_green_rewrote_while_an_unrelated_earlier_suite_repair_step_is_ticked_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    ledger = ".tdd/issue-9.md"
    repair = STEPS[0] + " ⟦suite-repair⟧"
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    (tmp_path / ledger).write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (repair, step, STEPS[2]))
    _commit(tmp_path, "A red, the suite-repair step ticked")
    (tmp_path / ledger).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (repair, step, STEPS[2]))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B ordinary green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_refuses_a_case_the_green_of_an_unticked_suite_repair_step_rewrote_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    ledger = ".tdd/issue-9.md"
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / ledger).write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (STEPS[0], step, repair))
    _commit(tmp_path, "A red, the suite-repair step listed but not ticked")
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B green of the unticked step, the ledger untouched")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


def _repair_green_fixture(tmp_path, run_cli, tests_frozen, monkeypatch, committed_repair):
    """The ledger passed to rerecord-refactored ticks a suite-repair step 3 whose green rewrote step A's case; the
    committed ledger holds that line only when `committed_repair`. Returns (ledger path, green sha)."""
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    repair = STEPS[2] + " ⟦suite-repair⟧"
    ticked = "# Plan\n\n- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair)
    if committed_repair:
        (tmp_path / ledger).write_text(ticked)
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B green")
    (tmp_path / ledger).write_text(ticked)
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    return ledger, green


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_refuses_a_green_when_the_committed_ledger_never_held_the_suite_repair_line_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    ledger, green = _repair_green_fixture(tmp_path, run_cli, tests_frozen, monkeypatch, False)

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_skips_an_unmapped_suite_repair_line_and_accepts_a_later_valid_one_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    repair = STEPS[2] + " ⟦suite-repair⟧"
    (tmp_path / ledger).write_text("- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, repair))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    # A ticked suite-repair line the committed ledger never held, ahead of the valid one (uncommitted).
    (tmp_path / ledger).write_text("- [x] ghost step ⟦suite-repair⟧\n" + (tmp_path / ledger).read_text())
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (0, 0)


@pytest.mark.process("a real git repository under tmp_path, its history walked from the green commit to HEAD")
def test_rerecord_refactored_refuses_a_case_a_later_commit_rewrote_again_after_a_suite_repair_green_3541(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    ledger, green = _repair_green_fixture(tmp_path, run_cli, tests_frozen, monkeypatch, True)
    suite = tmp_path / "test_suite.py"
    suite.write_text(suite.read_text().replace("    assert x\n", "    assert x == 1\n"))
    _commit(tmp_path, "C later rewrite that changes the assertion")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)
    kept = run_cli(tests_frozen, ["check-earlier", ledger, "--step", "step C"], cwd=tmp_path)[0]

    assert (code, _skip_lines(err, "test_suite.py test_one"), kept) == (1, 1, 1)


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_exits_0_for_a_case_a_later_replaces_case_step_names_in_a_pytest_suite_3624(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    replacing = "step B reverses it, replaces 'test_one' in test_suite.py ⟦replaces-case⟧"
    (tmp_path / ledger).write_text(
        "- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, replacing))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 7\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one")) == (0, 0)


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_exits_1_for_an_unnamed_case_a_green_rewrote_beside_a_case_a_replaces_case_step_names_3624(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    suite, step = tmp_path / "test_suite.py", STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    suite.write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1), BODY % ("two", 2)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_suite.py"], cwd=tmp_path)
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    replacing = "step B reverses it, replaces 'test_one' in test_suite.py ⟦replaces-case⟧"
    (tmp_path / ledger).write_text(
        "- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, replacing))
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 7\n").replace("x = 2\n", "x = 8\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_suite.py test_one"), _skip_lines(err, "test_suite.py test_two")) == (1, 0, 1)


@pytest.mark.process("a real git repository under tmp_path, its history and its committed ledger walked")
def test_rerecord_refactored_exits_1_for_a_same_named_case_in_another_suite_than_the_replaces_case_marker_names_3624(
        tmp_path, run_cli, tests_frozen, monkeypatch):
    step = STEPS[1]
    _plan_repo(tmp_path, monkeypatch)
    for suite in ("test_a.py", "test_b.py"):
        (tmp_path / suite).write_text("\n\n".join([CASE % ("base", 0), BODY % ("one", 1)]))
    run_cli(tests_frozen, ["record", "--step", step, "test_a.py", "test_b.py"], cwd=tmp_path)
    git(tmp_path, "add", "test_a.py", "test_b.py")
    _commit(tmp_path, "A red")
    ledger = ".tdd/issue-9.md"
    replacing = "step B reverses it, replaces 'test_one' in test_a.py ⟦replaces-case⟧"
    (tmp_path / ledger).write_text(
        "- [x] %s\n- [x] %s\n- [x] %s ⟂ refactor pending\n" % (STEPS[0], step, replacing))
    for suite in ("test_a.py", "test_b.py"):
        (tmp_path / suite).write_text((tmp_path / suite).read_text().replace("x = 1\n", "x = 7\n"))
    _commit(tmp_path, "B green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")

    code, _, err = run_cli(tests_frozen, ["rerecord-refactored", ledger, green], cwd=tmp_path)

    assert (code, _skip_lines(err, "test_a.py test_one"), _skip_lines(err, "test_b.py test_one")) == (1, 0, 1)

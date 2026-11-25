"""Cases for tick-ledger.sh that start the real entry point."""
import importlib
import os
import shutil
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("tick-ledger.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_ticks_the_relative_ledger_as_it_does_in_place(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    seed = "# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n"
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    for name in ("in-place", "caller"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "issue-42.md").write_text(seed)

    code, out, err = run_cli(tick_ledger, ["--refactor-pending", "issue-42.md", "collapse to single hyphen"],
                             cwd=tmp_path / "in-place")
    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "tick-ledger.sh"), "--refactor-pending",
                          "issue-42.md", "collapse to single hyphen"],
                         cwd=tmp_path / "caller", stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (code, out, err) == (0, "", "")
    assert (tmp_path / "caller" / "issue-42.md").read_bytes() == (tmp_path / "in-place" / "issue-42.md").read_bytes()
    assert "- [x] collapse to single hyphen ⟂ refactor pending\n" in (tmp_path / "caller" / "issue-42.md").read_text()


def git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                   capture_output=True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_a_diff_checked_step_rerecords_the_earlier_frozen_case_it_changed_so_check_earlier_passes_2199(
        tmp_path, run_cli, leave_receipt):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 1⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")

    leave_receipt(ledger, repo=tmp_path)
    ticked = run_cli(tick_ledger, [str(ledger), "diff-checked"], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (ticked, code, out) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_an_ordinary_step_that_only_mentions_the_diff_checked_tag_rerecords_nothing_2199(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two mentions ⟦diff-checked⟧ in prose ⟦criterion 5⟧", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")

    ticked = run_cli(tick_ledger, [str(ledger), "step two"], cwd=tmp_path)[0]
    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (ticked, rerecorded, code, "test_pinned_2199 (%s)" % earlier in out) == (0, 3, 1, True)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_an_ordinary_step_that_quotes_the_diff_checked_tag_ahead_of_a_criterion_marker_rerecords_nothing_2199(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit, later = (
        "step one adds a case", "step two quotes the tag ⟦diff-checked⟧ ⟦criterion 1⟧ in its prose ⟦criterion 5⟧",
        "step three adds another")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(tmp_path, "add", ".tdd/ledger.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")

    ticked = run_cli(tick_ledger, [str(ledger), "step two"], cwd=tmp_path)[0]
    rerecorded = run_cli(tests_frozen, ["rerecord-earlier", str(ledger), "--step", edit], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (ticked, rerecorded, code, "test_pinned_2199 (%s)" % earlier in out) == (0, 3, 1, True)


@pytest.mark.tree_audit("copies the lib and veri script directories")
@pytest.mark.process("the pinned snapshot's tick-ledger.sh and tests-frozen.sh, run beside a differing checkout copy")
def test_the_diff_checked_tick_digests_the_rerecorded_case_with_the_snapshot_tests_frozen_not_the_checkouts_2199(
        tmp_path, leave_receipt):
    repo, snapshot = tmp_path / "repo", tmp_path / "snapshot"
    checkout = repo / "skills/tdd/scripts"
    for target in (snapshot, checkout):
        for name in ("lib", "veri"):
            shutil.copytree(SCRIPTS / name, target / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("tick-ledger.sh", "tests-frozen.sh"):
            shutil.copy(SCRIPTS / name, target / name)
    digest = checkout / "veri/tests_frozen.py"
    digest.write_text(digest.read_text().replace("hashlib.sha256(body.encode())", "hashlib.sha256(b'x' + body.encode())"))
    (repo / "tests").mkdir()
    (repo / ".tdd").mkdir()
    (repo / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(repo, "init", "-q")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "base")
    earlier, edit, later = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 4⟧", "step three adds another"
    (repo / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")

    def snap(script, *argv):
        done = subprocess.run([str(snapshot / script), *argv], cwd=repo, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True)
        return done.returncode, done.stdout

    snap("tests-frozen.sh", "record", "--step", earlier, "tests/test_suite.py")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "red")
    ledger = repo / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
    git(repo, "add", ".tdd/ledger.md")
    git(repo, "commit", "-q", "-m", "ledger")
    (repo / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(repo, "add", "tests")
    git(repo, "commit", "-q", "-m", "edit")

    leave_receipt(ledger, repo=repo)
    ticked = snap("tick-ledger.sh", str(ledger), "diff-checked")[0]
    checked = snap("tests-frozen.sh", "check-earlier", str(ledger), "--step", later)

    assert (ticked, *checked) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, committed after a diff-checked tick")
def test_committing_the_ledger_after_a_diff_checked_tick_leaves_the_tree_clean_2199(tmp_path, run_cli, leave_receipt):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".gitignore").write_text(".tdd/*\n!.tdd/issue-*.md\n")
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", ".gitignore", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    earlier, edit = "step one adds a case", "step two ⟦diff-checked⟧ ⟦criterion 8⟧"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/issue-7.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n" % (earlier, edit))
    git(tmp_path, "add", ".tdd/issue-7.md")
    git(tmp_path, "commit", "-q", "-m", "ledger")
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "edit")

    leave_receipt(ledger, repo=tmp_path)
    ticked = run_cli(tick_ledger, [str(ledger), "diff-checked"], cwd=tmp_path)[0]
    git(tmp_path, "add", ".tdd/issue-7.md")
    git(tmp_path, "commit", "-q", "-m", "tick")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_path, capture_output=True, text=True).stdout

    assert (ticked, status) == (0, "")


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_a_step_refactor_pending_records_a_case_renamed_after_its_freeze_under_its_committed_title_2825(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "tests/test_suite.py").write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step adds a case"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_before_rename_2825():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_after_rename_2825():\n    assert 1 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "green")

    ticked = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path)[0]

    titles = sorted(line.split("\t")[1] for record in (tmp_path / ".tdd").glob("tests-frozen-*.record")
                    for line in record.read_text().splitlines() if line.startswith("body: "))
    assert (ticked, titles) == (0, ["test_after_rename_2825"])


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_refactor_pending_leaves_a_record_unwritten_when_a_recorded_case_is_missing_with_no_fresh_one_2825(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step adds a case"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_kept_2825():\n    assert 1 == 2\n"
                     "\n\ndef test_gone_2825():\n    assert 1 == 3\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_kept_2825():\n    assert 1 == 2\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "green")
    records = list((tmp_path / ".tdd").glob("tests-frozen-*.record"))
    for record in records:
        os.utime(record, ns=(1_000_000_000, 1_000_000_000))
    before = [(record.read_text(), record.stat().st_mtime_ns) for record in records]

    ticked = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path)[0]

    assert (ticked, [(record.read_text(), record.stat().st_mtime_ns) for record in records]) == (0, before)


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_a_step_refactor_pending_records_a_case_renamed_only_in_the_work_tree_under_its_new_title_2825(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step adds a case"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_before_rename_2825():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_after_rename_2825():\n    assert 1 == 2\n")

    ticked = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path)[0]

    titles = sorted(line.split("\t")[1] for record in (tmp_path / ".tdd").glob("tests-frozen-*.record")
                    for line in record.read_text().splitlines() if line.startswith("body: "))
    assert (ticked, titles) == (0, ["test_after_rename_2825"])


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_refactor_pending_from_a_subdirectory_records_a_work_tree_renamed_case_under_its_new_title_2917(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "nested").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step adds a case"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_pinned_2917():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_renamed_2917():\n    assert 1 == 2\n")

    ticked = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path / "nested")[0]

    titles = sorted(line.split("\t")[1] for record in (tmp_path / ".tdd").glob("tests-frozen-*.record")
                    for line in record.read_text().splitlines() if line.startswith("body: "))
    assert (ticked, titles) == (0, ["test_renamed_2917"])


@pytest.mark.process("two real git repositories under tmp_path, asked which test files differ from HEAD")
def test_ticking_refactor_pending_from_a_subdirectory_and_from_the_root_leaves_byte_identical_records_2917(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    step = "step adds a case"

    def tick_after_rename(name, cwd_sub):
        repo = tmp_path / name
        (repo / "tests").mkdir(parents=True)
        (repo / ".tdd").mkdir()
        (repo / "nested").mkdir()
        suite = repo / "tests/test_suite.py"
        suite.write_text("def test_older_case():\n    assert True\n")
        git(repo, "init", "-q")
        git(repo, "add", "tests")
        git(repo, "commit", "-q", "-m", "base")
        ledger = repo / ".tdd/ledger.md"
        ledger.write_text("- [ ] %s\n" % step)
        suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_pinned_2917():\n    assert 1 == 2\n")
        run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=repo)
        suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_renamed_2917():\n    assert 1 == 2\n")
        run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=repo / cwd_sub)
        return sorted((repo / ".tdd").glob("tests-frozen-*.record"))

    from_root = tick_after_rename("root", ".")
    from_nested = tick_after_rename("sub", "nested")

    assert [r.name for r in from_nested] == [r.name for r in from_root]
    assert [r.read_bytes() for r in from_nested] == [r.read_bytes() for r in from_root]
    assert b"test_renamed_2917" in from_nested[0].read_bytes()


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_pairs_each_work_tree_renamed_case_with_its_missing_title_by_body_not_by_position_2825(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step adds two cases"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    suite.write_text("def test_older_case():\n    assert True\n\n\n"
                     "def test_first_before_2825():\n    assert 1 == 2\n\n\n"
                     "def test_second_before_2825():\n    assert 3 == 4\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_older_case():\n    assert True\n\n\n"
                     "def test_second_after_2825():\n    assert 3 == 4\n\n\n"
                     "def test_first_after_2825():\n    assert 1 == 2\n")

    ticked = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path)[0]

    recorded = [line.split("\t") for record in (tmp_path / ".tdd").glob("tests-frozen-*.record")
                for line in record.read_text().splitlines() if line.startswith("body: ")]
    assert (ticked, [title for _, title, _ in recorded]) == (0, ["test_first_after_2825", "test_second_after_2825"])


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_does_not_pair_a_missing_title_with_a_case_already_committed_in_head_2825(tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_committed_2825():\n    assert 5 == 6\n")
    git(tmp_path, "commit", "-q", "-a", "-m", "an earlier step's case")
    step = "step adds a case"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_committed_2825():\n    assert 5 == 6\n\n\n"
                     "def test_before_rename_2825():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_committed_2825():\n    assert 5 == 6\n\n\n"
                     "def test_after_rename_2825():\n    assert 1 == 3\n")

    ticked = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path)[0]

    titles = sorted(line.split("\t")[1] for record in (tmp_path / ".tdd").glob("tests-frozen-*.record")
                    for line in record.read_text().splitlines() if line.startswith("body: "))
    assert (ticked, titles) == (0, ["test_after_rename_2825"])


@pytest.mark.process("a real git repository under tmp_path, asked which test files differ from HEAD")
def test_ticking_refactor_pending_refuses_to_pair_two_renamed_cases_by_file_position_2913(
        tmp_path, run_cli):
    tick_ledger = importlib.import_module("veri.tick_ledger")
    tests_frozen = importlib.import_module("veri.tests_frozen")
    (tmp_path / "tests").mkdir()
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "tests/test_suite.py"
    suite.write_text("def test_older_case():\n    assert True\n")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "base")
    step = "step adds two cases"
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [ ] %s\n" % step)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_alpha_2913():\n    assert 1 == 2\n"
                     "\n\ndef test_beta_2913():\n    assert 3 == 4\n")
    run_cli(tests_frozen, ["record", "--step", step, "tests/test_suite.py"], cwd=tmp_path)
    suite.write_text("def test_older_case():\n    assert True\n\n\ndef test_beta_renamed_2913():\n    assert 30 == 40\n"
                     "\n\ndef test_alpha_renamed_2913():\n    assert 10 == 20\n")
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "green")
    records = list((tmp_path / ".tdd").glob("tests-frozen-*.record"))
    before = [record.read_bytes() for record in records]

    ticked, _, err = run_cli(tick_ledger, ["--refactor-pending", str(ledger), step], cwd=tmp_path)

    assert (ticked, [record.read_bytes() for record in records],
            records[0].name in err, "test_alpha_2913" in err or "test_beta_2913" in err) \
        == (2, before, True, True)

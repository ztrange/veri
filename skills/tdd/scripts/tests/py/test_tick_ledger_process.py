"""Cases for tick-ledger.sh that start the real entry point."""
import importlib
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
        tmp_path, run_cli):
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


@pytest.mark.tree_audit("copies the lib and veri script directories")
@pytest.mark.process("the pinned snapshot's tick-ledger.sh and tests-frozen.sh, run beside a differing checkout copy")
def test_the_diff_checked_tick_digests_the_rerecorded_case_with_the_snapshot_tests_frozen_not_the_checkouts_2199(
        tmp_path):
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

    ticked = snap("tick-ledger.sh", str(ledger), "diff-checked")[0]
    checked = snap("tests-frozen.sh", "check-earlier", str(ledger), "--step", later)

    assert (ticked, *checked) == (0, 0, "")


@pytest.mark.process("a real git repository under tmp_path, committed after a diff-checked tick")
def test_committing_the_ledger_after_a_diff_checked_tick_leaves_the_tree_clean_2199(tmp_path, run_cli):
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

    ticked = run_cli(tick_ledger, [str(ledger), "diff-checked"], cwd=tmp_path)[0]
    git(tmp_path, "add", ".tdd/issue-7.md")
    git(tmp_path, "commit", "-q", "-m", "tick")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_path, capture_output=True, text=True).stdout

    assert (ticked, status) == (0, "")

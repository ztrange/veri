"""Cases for tick-ledger.sh that start the real entry point."""
import importlib
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
    earlier, edit, later = "step one adds a case", "⟦diff-checked⟧ step two", "step three adds another"
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 1 == 2\n")
    run_cli(tests_frozen, ["record", "--step", earlier, "tests/test_suite.py"], cwd=tmp_path)
    git(tmp_path, "add", "tests")
    git(tmp_path, "commit", "-q", "-m", "red")
    ledger = tmp_path / ".tdd/ledger.md"
    ledger.write_text("- [x] %s\n- [ ] %s\n- [ ] %s\n" % (earlier, edit, later))
    (tmp_path / "tests/test_suite.py").write_text(
        "def test_older_case():\n    assert True\n\n\ndef test_pinned_2199():\n    assert 2 == 2\n")

    ticked = run_cli(tick_ledger, [str(ledger), "diff-checked"], cwd=tmp_path)[0]
    code, out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", later], cwd=tmp_path)

    assert (ticked, code, out) == (0, 0, "")

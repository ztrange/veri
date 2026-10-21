"""Cases for refactor-budget.sh that start a real process: a symlinked entry point, git over the tree."""
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parents[5]
IN_PLACE = SKILL_DIR / "scripts" / "refactor-budget.sh"


def without_budgets(monkeypatch):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    monkeypatch.delenv("VERI_ISSUE_REFACTOR_BUDGET", raising=False)


@pytest.mark.tree_audit("every tracked file outside the docs and .tdd trees, read by git grep")
@pytest.mark.process("git grep over the repository this suite runs in")
def test_no_tracked_file_outside_the_docs_and_tdd_trees_states_3_as_the_veri_issue_refactor_budget_default():
    stale = "VERI_ISSUE_REFACTOR_BUDGET(:-|[^0-9]{0,40}default[^0-9]{0,4})3([^0-9]|$)"
    hits = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-nE", stale, "--", ".", ":!docs", ":!projects/docs", ":!.tdd"],
        capture_output=True, text=True).stdout
    assert hits == "", "want no statement of default 3 for VERI_ISSUE_REFACTOR_BUDGET, found:\n" + hits


@pytest.mark.process("refactor-budget.sh run through a symlink to the skill directory from another working directory")
def test_a_shim_run_through_a_symlink_and_from_another_cwd_answers_as_in_place(tmp_path, monkeypatch):
    without_budgets(monkeypatch)
    (tmp_path / "linked-skill").symlink_to(SKILL_DIR, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    problems = []
    for count, want_code, want_out in (
            ("4", 0, b"refactor 4/5 \xe2\x80\x94 another transform may run\n"),
            ("5", 3, b"refactor 5/5 \xe2\x80\x94 budget spent\n"),
            ("ten", 2, b"")):
        in_place = subprocess.run([str(IN_PLACE), count], capture_output=True)
        linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "refactor-budget.sh"), count],
                                cwd=tmp_path / "elsewhere", capture_output=True)
        if (linked.stdout, linked.returncode) != (want_out, want_code):
            problems.append(f"count {count} linked: want exit {want_code} and {want_out!r}, "
                            f"got exit {linked.returncode} and {linked.stdout!r}")
        if (linked.stdout, linked.returncode) != (in_place.stdout, in_place.returncode):
            problems.append(f"count {count}: linked answered exit {linked.returncode} {linked.stdout!r}, "
                            f"in place exit {in_place.returncode} {in_place.stdout!r}")
    assert problems == []

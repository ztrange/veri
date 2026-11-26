"""How skills/tdd/SKILL.md's preflight checks launchability, budgets, GitHub, the worktree baseline and the conductor.pid lock, read as text."""
import pathlib
import subprocess

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[2].parent / "SKILL.md"

REBASE_CALL = "rebase-onto-default.sh"


SCRIPTS = SKILL.parent / "scripts"


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def new_repo(path, *args):
    subprocess.run(["git", "init", "-q", "-b", "main", *args, str(path)], cwd=path.parent, check=True, capture_output=True)
    if "--bare" not in args:
        git(path, "config", "user.name", "Test")
        git(path, "config", "user.email", "test@example.com")


def commit_all(path, message):
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", message)


def run_discard(wt):
    return subprocess.run([str(SCRIPTS / "resume-clean.sh")], cwd=wt, capture_output=True, text=True)


def discard_stray(wt):
    return run_discard(wt).stdout


@pytest.mark.process("git: a bash-run discard block in a clone, then rebase-onto-default.sh over the default branch's new file")
def test_1420_skill_md_s_preflight_discard_removes_a_killed_leaf_s_untracked_file_at_a_path_the_default_branch_has_since_added_so_the_resume_rebase_onto_default_sh_exits_0_not_2(tmp_path):
    origin, seed, wt = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "wt"
    new_repo(origin, "--bare")
    new_repo(seed)
    (seed / "file.txt").write_text("base\n")
    commit_all(seed, "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(wt)], cwd=tmp_path, check=True, capture_output=True)
    git(wt, "config", "user.name", "veri")
    git(wt, "config", "user.email", "veri@example.test")
    git(wt, "checkout", "-q", "-b", "tdd/1-a-run")
    (wt / "work.txt").write_text("the run's work\n")
    commit_all(wt, "feat: a step's green commit (#1)")
    (seed / "other.txt").write_text("another run's work\n")
    commit_all(seed, "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    git(wt, "fetch", "-q", "origin")
    (wt / "other.txt").write_text("a killed leaf's half-written file\n")
    run_discard(wt)
    rebase = subprocess.run(["bash", str(SCRIPTS / REBASE_CALL)], cwd=wt, capture_output=True, text=True)
    assert rebase.returncode == 0, f"{REBASE_CALL} after the discard block, exit: want 0, got {rebase.returncode} - stderr: {rebase.stderr}"


@pytest.mark.process("git: a bash-run discard block in a repository holding an untracked file")
def test_1420_skill_md_s_preflight_discard_captures_a_killed_leaf_s_untracked_file_in_stray_before_removing_it_so_the_resuming_comment_names_it(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / "file.txt").write_text("base\n")
    commit_all(wt, "initial")
    (wt / "other.txt").write_text("a killed leaf's half-written file\n")
    got = discard_stray(wt)
    assert "?? other.txt" in got.splitlines(), f"$stray does not list the untracked file: want a line '?? other.txt', got: {got}"


@pytest.mark.process("git: a bash-run discard block in a repository whose .gitignore names .tdd/")
def test_1420_skill_md_s_preflight_discard_never_removes_a_file_gitignore_ignores_so_a_tdd_leaf_log_survives_it(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / ".gitignore").write_text(".tdd/\n")
    commit_all(wt, "initial")
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-1-leaf.log").write_text("a leaf's log\n")
    run_discard(wt)
    assert (wt / ".tdd" / "issue-1-leaf.log").is_file(), "the discard block removed the ignored run-state file .tdd/issue-1-leaf.log"


@pytest.mark.process("git: a bash-run discard block under the repository's own .tdd ignore patterns")
def test_1420_skill_md_s_preflight_discard_never_loses_an_untracked_tdd_run_state_file_the_real_gitignore_un_ignores_the_refactor_owed_file_survives_uncaptured(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / ".gitignore").write_text(".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n")
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-1.md").write_text("- [x] step one\n")
    commit_all(wt, "initial")
    (wt / ".tdd" / "issue-1-refactor-owed.md").write_text("a refactor the run owes\n")
    got = discard_stray(wt)
    assert (wt / ".tdd" / "issue-1-refactor-owed.md").is_file(), "the discard block removed the untracked run-state file .tdd/issue-1-refactor-owed.md"
    assert "issue-1-refactor-owed.md" not in got, f"$stray captures the run-state file as a stray: {got}"

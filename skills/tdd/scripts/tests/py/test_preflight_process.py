"""Cases for veri/preflight.py that start a real process: detach-command.sh itself, not a fake of it."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, git, new_repo, origin_head_at


@pytest.fixture
def detached(tmp_path, monkeypatch):
    """preflight.detached in a scratch run directory; every script it names is really run, and its argv kept in `.seen`."""
    preflight = importlib.import_module("veri.preflight")
    (tmp_path / ".tdd").mkdir()
    seen = []

    def run_script(name, *args, cwd=None, env=None):
        seen.append((os.path.basename(name), *args))
        proc = subprocess.run([name, *args], capture_output=True, text=True, cwd=cwd, env=env)
        return proc.returncode, proc.stdout, proc.stderr

    monkeypatch.setattr(preflight, "run_script", run_script)

    def call(name, cmd):
        return preflight.detached(name, cmd, str(tmp_path), dict(os.environ, VERI_POLL="0.05"))

    call.seen = seen
    return call


@pytest.mark.process("the real detach-command.sh, starting and waiting on a detached sh")
def test_a_tier_command_of_several_words_is_run_by_the_real_detach_command_and_its_output_is_recorded(tmp_path, detached):
    code = detached("probe", "sh -c 'echo two words'")

    tdd = tmp_path / ".tdd"
    assert (code, (tdd / "probe.exit").read_text().strip(), (tdd / "probe.out").read_text()) == (0, "0", "two words\n")
    assert detached.seen[0] == ("detach-command.sh", "start", "probe", "sh", "-c", "echo two words")


@pytest.mark.process("the real detach-command.sh, starting and waiting on a detached sh that fails")
def test_a_tier_command_that_fails_comes_back_non_zero_from_the_real_detach_command(tmp_path, detached):
    code = detached("red", "sh -c 'exit 7'")

    assert (code != 0, (tmp_path / ".tdd" / "red.exit").read_text().strip()) == (True, "7")


def set_up_in(repo, monkeypatch):
    """preflight.set_up in <repo>, a resume when its ledger is committed: git and detect-test-command.sh really run there,
    every other script answers 0 (issue-worktree.sh with <repo>, gh with an empty issue body); returns (exit code, fast
    command)."""
    preflight = importlib.import_module("veri.preflight")

    def run_script(name, *args, cwd=None, env=None):
        base = os.path.basename(name)
        if base == "issue-worktree.sh":
            return 0, str(repo) + "\n", ""
        if base in ("git", "detect-test-command.sh"):
            proc = subprocess.run([name, *args], capture_output=True, text=True, cwd=cwd, env=env)
            return proc.returncode, proc.stdout, proc.stderr
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    try:
        return 0, preflight.set_up("12", "slug", str(SCRIPTS / "detect-test-command.sh"))[1]
    except preflight.Stop as stop:
        return stop.code, None


@pytest.mark.process("git init, commit, checkout, update-ref and symbolic-ref run for real in a scratch repository, then"
                     " preflight.set_up's git and detect-test-command.sh calls in it")
def test_a_resumed_run_reads_its_fast_command_at_the_branch_base_never_a_claude_md_the_branch_committed_4263(
        tmp_path, monkeypatch):
    repo = new_repo(tmp_path / "repo")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    origin_head_at(repo)
    git(repo, "checkout", "-q", "-b", "issue-12")
    commit_all(repo, "ledger and an edited fast line", **{".tdd__issue-12.md": "- [x] step\n",
                                                          "CLAUDE.md": "veri: fast tests: true\n"})
    (repo / ".tdd" / "issue-12-branch-base").write_text(base + "\n")

    assert set_up_in(repo, monkeypatch) == (0, "pytest -q")


@pytest.mark.process("git init and commit run for real in a scratch repository with no origin/HEAD, then"
                     " preflight.set_up's git and detect-test-command.sh calls in it")
def test_a_fresh_run_with_no_branch_base_stops_with_exit_2_never_reading_the_working_trees_fast_command_4263(
        tmp_path, monkeypatch):
    repo = new_repo(tmp_path / "repo")
    commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})

    assert set_up_in(repo, monkeypatch) == (2, None)


@pytest.mark.process("git init, commit, checkout, update-ref and symbolic-ref run for real in a scratch repository, then"
                     " preflight.set_up's git and detect-test-command.sh calls in it")
def test_a_fresh_launch_records_the_merge_base_of_head_and_origin_head_and_reads_its_fast_command_there_4374(
        tmp_path, monkeypatch):
    repo = new_repo(tmp_path / "repo")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    origin_head_at(repo)
    git(repo, "checkout", "-q", "-b", "issue-12")
    commit_all(repo, "an edited fast line", **{"CLAUDE.md": "veri: fast tests: true\n"})
    record = repo / ".tdd" / "issue-12-branch-base"

    answer = set_up_in(repo, monkeypatch)

    assert (answer, record.read_text() if record.exists() else None) == ((0, "pytest -q"), base + "\n")


@pytest.mark.process("git init, commit, checkout, update-ref and symbolic-ref run for real in a scratch repository, then"
                     " preflight.set_up's git and detect-test-command.sh calls in it")
def test_a_resume_reads_its_fast_command_at_the_recorded_base_never_at_the_merge_base_of_a_rewritten_origin_head_4374(
        tmp_path, monkeypatch):
    repo = new_repo(tmp_path / "repo")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    origin_head_at(repo)
    git(repo, "checkout", "-q", "-b", "issue-12")
    rewritten = commit_all(repo, "a leaf's fast line", **{"CLAUDE.md": "veri: fast tests: true\n"})
    commit_all(repo, "ledger", **{".tdd__issue-12.md": "- [x] step\n"})
    (repo / ".tdd" / "issue-12-branch-base").write_text(base + "\n")
    git(repo, "update-ref", "refs/remotes/origin/main", rewritten)

    assert set_up_in(repo, monkeypatch) == (0, "pytest -q")

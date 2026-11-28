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
def test_a_compound_tier_command_is_run_by_the_real_detach_command_through_a_shell_and_its_output_is_recorded_4856(
        tmp_path, detached):
    code = detached("probe", "echo two words && echo more")

    tdd = tmp_path / ".tdd"
    assert (code, (tdd / "probe.exit").read_text().strip(), (tdd / "probe.out").read_text()) == (0, "0",
                                                                                                 "two words\nmore\n")
    assert detached.seen[0] == ("detach-command.sh", "start", "probe", "sh", "-c", "echo two words && echo more")


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
        set_up_in.stop = stop
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
    record = repo / ".tdd" / "issue-12-branch-base"

    assert (set_up_in(repo, monkeypatch), record.exists()) == ((2, None), False)


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
def test_a_fresh_stacked_launch_records_the_merge_base_with_the_stack_it_was_cut_from_as_a_rebase_does_4374(
        tmp_path, monkeypatch):
    repo = new_repo(tmp_path / "repo")
    claude = "veri: fast tests: pytest -q\nveri: stack branch: stack\n"
    commit_all(repo, "base", **{"CLAUDE.md": claude})
    origin_head_at(repo)
    stack = commit_all(repo, "the stack's work", **{"stacked.txt": "joined\n"})
    git(repo, "update-ref", "refs/remotes/origin/stack", stack)
    git(repo, "checkout", "-q", "-b", "issue-12")
    commit_all(repo, "an edited fast line", **{"CLAUDE.md": claude.replace("pytest -q", "true")})
    (repo / ".tdd").mkdir(exist_ok=True)
    (repo / ".tdd" / "issue-12-base").write_text("stack\n")
    record = repo / ".tdd" / "issue-12-branch-base"

    answer = set_up_in(repo, monkeypatch)

    assert (answer, record.read_text() if record.exists() else None) == ((0, "pytest -q"), stack + "\n")


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


@pytest.mark.process("git init, commit, checkout, update-ref and symbolic-ref run for real in a scratch repository, then"
                     " preflight.set_up's git and detect-test-command.sh calls in it")
@pytest.mark.parametrize("record", ["missing", "unreadable", "origin/main", "off-branch", "deadbeef"])
def test_a_resume_whose_branch_base_record_is_missing_unreadable_not_hex_or_not_an_ancestor_stops_with_exit_2_naming_it_4374(
        tmp_path, monkeypatch, record):
    repo = new_repo(tmp_path / "repo")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    origin_head_at(repo)
    git(repo, "checkout", "-q", "-b", "side")
    side = commit_all(repo, "off the branch", **{"side": "x\n"})
    git(repo, "checkout", "-q", "-b", "issue-12", base)
    commit_all(repo, "ledger", **{".tdd__issue-12.md": "- [x] step\n"})
    path = repo / ".tdd" / "issue-12-branch-base"
    if record == "unreadable":
        path.mkdir()
    elif record != "missing":
        path.write_text((side if record == "off-branch" else record) + "\n")

    code = set_up_in(repo, monkeypatch)
    what = set_up_in.stop.what if code[0] else None

    assert (code, what and str(path) in what) == ((2, None), True)


def carry_on_origin(repo, issue, text):
    """Give <repo> a bare origin whose refs/veri/runs/<issue> holds `.tdd/issue-<issue>-branch-base` as <text>, or
    no such ref when <text> is None."""
    origin = repo.parent / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], cwd=repo.parent, check=True, capture_output=True)
    git(repo, "remote", "add", "origin", str(origin))
    if text is None:
        return

    def plumb(*args, data):
        return subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, text=True,
                              check=True).stdout.strip()

    blob = plumb("hash-object", "-w", "--stdin", data=text)
    inner = plumb("mktree", data="100644 blob %s\tissue-%s-branch-base\n" % (blob, issue))
    outer = plumb("mktree", data="040000 tree %s\t.tdd\n" % inner)
    records = git(repo, "commit-tree", outer, "-m", "records")
    git(repo, "push", "-q", "origin", "%s:refs/veri/runs/%s" % (records, issue))


@pytest.mark.process("git init, commit, checkout, update-ref, symbolic-ref and a push to a bare origin run for real in a"
                     " scratch repository, then preflight.set_up's git, fetch and detect-test-command.sh calls in it")
@pytest.mark.parametrize("carried", ["base", "origin/main", "off-branch", None])
def test_a_resume_with_no_local_record_restores_the_carried_branch_base_only_when_hex_and_an_ancestor_of_head_4374(
        tmp_path, monkeypatch, carried):
    repo = new_repo(tmp_path / "repo")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    origin_head_at(repo)
    git(repo, "checkout", "-q", "-b", "side")
    side = commit_all(repo, "off the branch", **{"side": "x\n"})
    git(repo, "checkout", "-q", "-b", "issue-12", base)
    rewritten = commit_all(repo, "a leaf's fast line", **{"CLAUDE.md": "veri: fast tests: true\n"})
    commit_all(repo, "ledger", **{".tdd__issue-12.md": "- [x] step\n"})
    git(repo, "update-ref", "refs/remotes/origin/main", rewritten)
    carry_on_origin(repo, "12", None if carried is None else {"base": base, "off-branch": side}.get(carried, carried) + "\n")
    path = repo / ".tdd" / "issue-12-branch-base"

    answer = set_up_in(repo, monkeypatch)
    named = str(path) in set_up_in.stop.what if answer[0] else None

    assert (answer, named, path.read_text() if path.exists() else None) == (
        ((0, "pytest -q"), None, base + "\n") if carried == "base" else ((2, None), True, None))


@pytest.mark.process("git init, commit, checkout, update-ref, symbolic-ref and a push to a bare origin run for real in a"
                     " scratch repository, then preflight.set_up's git, fetch and detect-test-command.sh calls in it")
def test_a_resume_whose_local_record_is_unreadable_stops_with_exit_2_never_restoring_the_carried_one_4374(
        tmp_path, monkeypatch):
    repo = new_repo(tmp_path / "repo")
    base = commit_all(repo, "base", **{"CLAUDE.md": "veri: fast tests: pytest -q\n"})
    origin_head_at(repo)
    git(repo, "checkout", "-q", "-b", "issue-12")
    commit_all(repo, "ledger", **{".tdd__issue-12.md": "- [x] step\n"})
    carry_on_origin(repo, "12", base + "\n")
    path = repo / ".tdd" / "issue-12-branch-base"
    path.mkdir()

    answer = set_up_in(repo, monkeypatch)

    assert (answer, answer[0] and str(path) in set_up_in.stop.what, path.is_dir()) == ((2, None), True, True)

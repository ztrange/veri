"""Cases for push-branch.sh, driven through its command-line interface."""
import importlib
import json
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, git, new_repo

BRANCH = "tdd/191-run-commits-live-on-one-disk"
SHA = "a" * 40
LANDED_ENV = {"VERI_ISSUE": "191", "VERI_ACTOR": "conductor", "VERI_PUSH_BACKOFF": "0", "VERI_STEP": "a step"}


@pytest.fixture
def push_branch():
    return importlib.import_module("veri.push_branch")


@pytest.fixture(autouse=True)
def no_pointer_comment(monkeypatch):
    """The pointer comment a landed push writes goes to GitHub, which no case here reaches: recorded, not made."""
    pointer_comment = importlib.import_module("veri.pointer_comment")
    monkeypatch.setattr(pointer_comment, "after_push", lambda: None)


def run_repo(path, remote=None, branch=BRANCH):
    new_repo(path)
    commit_all(path, "initial", allow_empty=True)
    git(path, "checkout", "-q", "-b", branch)
    commit_all(path, "feat: a step's green commit (#191)",
               **{".tdd__issue-191.md": "\n- [x] a step ⟂ refactor pending\n- [ ] the next step\n"})
    if remote is not None:
        git(path, "remote", "add", "origin", str(remote))
    return path


def bare(path):
    path.mkdir()
    git(path, "init", "-q", "--bare", "-b", "main")
    return path


def remote_at(remote, branch=BRANCH):
    done = subprocess.run(["git", "-C", str(remote), "rev-parse", "--verify", "-q", "refs/heads/%s" % branch],
                          capture_output=True, text=True)
    return done.stdout.strip() or "<absent>"


@pytest.mark.process("git push to an origin that cannot be reached")
def test_a_failing_push_exits_0_leaving_head_the_commit_count_and_the_ledger_unchanged_and_records_push_failed(
        tmp_path, run_cli, push_branch, events):
    repo = run_repo(tmp_path / "run", tmp_path / "no-such-remote.git")
    ledger = repo / ".tdd" / "issue-191.md"
    before = (git(repo, "rev-parse", "HEAD"), git(repo, "rev-list", "--count", "HEAD"), ledger.read_text())

    code, out, err = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    assert code == 0
    assert (git(repo, "rev-parse", "HEAD"), git(repo, "rev-list", "--count", "HEAD"), ledger.read_text()) == before
    assert [(r["event"], r.get("attempts"), r.get("stage"), r.get("status"), r["issue"]) for r in events.records(repo)] == [
        ("stage-start", None, "push", None, "191"), ("push-failed", "4", None, None, "191"),
        ("stage-end", None, "push", "0", "191")]


@pytest.mark.process("git push to a bare repository")
def test_a_push_that_lands_leaves_the_branch_on_the_remote_at_the_commit_head_is_on(tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "landed", remote)

    code, out, err = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    assert code == 0
    assert remote_at(remote) == git(repo, "rev-parse", "HEAD")


@pytest.mark.process("git push of a branch and a side ref to a bare repository")
def test_a_push_that_lands_also_pushes_refs_veri_runs_n_a_commit_on_no_branch_holding_the_runs_journal_lines_skill_pin_and_timeout_pin(
        tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "records", remote)
    lines = ['{"issue": "191", "event": "start"}', '{"issue": "192", "event": "start"}', '{"issue": "191", "event": "step-start"}']
    (repo / ".tdd" / "events.jsonl").write_text("".join(line + "\n" for line in lines))
    (repo / ".tdd" / "issue-191-skill-commit").write_text("abc1234\n")
    (repo / ".tdd" / "issue-191-timeout").write_text("3600\n")

    code, _, _ = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    ref = "refs/veri/runs/191"
    shown = {name: subprocess.run(["git", "-C", str(remote), "show", "%s:.tdd/%s" % (ref, name)],
                                  capture_output=True, text=True).stdout
             for name in ("events.jsonl", "issue-191-skill-commit", "issue-191-timeout")}
    on_a_branch = subprocess.run(["git", "-C", str(remote), "branch", "--contains", ref],
                                 capture_output=True, text=True).stdout.strip()
    carried = shown["events.jsonl"].splitlines()
    under_way = json.loads(carried.pop())  # the push's own stage-start, written before it (#4230)
    shown["events.jsonl"] = "".join(line + "\n" for line in carried)
    assert (under_way["event"], under_way["stage"]) == ("stage-start", "push")
    assert (code, shown, on_a_branch) == (0, {
        "events.jsonl": lines[0] + "\n" + lines[2] + "\n",
        "issue-191-skill-commit": "abc1234\n",
        "issue-191-timeout": "3600\n",
    }, "")


def test_a_non_fast_forward_rejection_exits_1_after_one_attempt_naming_the_remote_sha_and_recording_push_rejected(
        tmp_path, run_cli, push_branch, events, fake_processes):
    (tmp_path / ".git").mkdir()
    rejected = " ! [rejected]        HEAD -> %s (non-fast-forward)\n" % BRANCH

    def answer(line, **kwargs):
        if line.startswith("git push"):
            return 1, rejected, ""
        if line == "git rev-parse --abbrev-ref HEAD":
            return 0, BRANCH + "\n", ""
        if line.startswith("git ls-remote"):
            return 0, "%s\trefs/heads/%s\n" % (SHA, BRANCH), ""
        raise AssertionError("unexpected process: " + line)

    calls = fake_processes(answer)

    code, out, err = run_cli(push_branch, [], env={**LANDED_ENV, "VERI_ISSUE": "232"}, cwd=tmp_path)

    assert code == 1
    assert len([c for c in calls if c.startswith("git push")]) == 1
    assert SHA in err
    assert [(r["event"], r.get("remote_sha"), r.get("status")) for r in events.records(tmp_path)] == [
        ("stage-start", None, None), ("push-rejected", SHA, None), ("stage-end", None, "1")]


@pytest.mark.process("git push to a bare repository")
def test_a_push_that_lands_exits_0_writes_nothing_to_stderr_and_appends_only_its_push_stage(
        tmp_path, run_cli, push_branch, events):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "quiet", remote)

    code, out, err = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    assert (code, out, err) == (0, "", "")
    assert [(r["event"], r["stage"], r.get("status"), r["issue"]) for r in events.records(repo)] == [
        ("stage-start", "push", None, "191"), ("stage-end", "push", "0", "191")]


def test_a_push_to_a_missing_origin_sleeps_the_backoff_the_case_sets_and_never_the_default(
        tmp_path, run_cli, push_branch, events, fake_processes):
    (tmp_path / ".git").mkdir()

    def answer(line, **kwargs):
        return (1, "fatal: no such remote\n", "") if line.startswith("git push") else (0, "", "")

    calls = fake_processes(answer)

    code, out, err = run_cli(push_branch, [], env={**LANDED_ENV, "VERI_PUSH_RETRIES": "2"}, cwd=tmp_path)

    assert code == 0
    assert [c for c in calls if c.startswith("sleep")] == ["sleep 0", "sleep 0"]


@pytest.mark.process("git push --force-with-lease to a bare repository")
def test_force_with_lease_replaces_a_remote_still_at_the_sha_refuses_one_that_has_moved_on_and_with_no_argument_replaces_nothing(
        tmp_path, run_cli, push_branch):
    branch = "tdd/238-lease"
    env = {**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}

    def fixture(name):
        remote = bare(tmp_path / ("origin-%s.git" % name))
        repo = run_repo(tmp_path / name, remote, branch)
        git(repo, "push", "-q", "origin", branch)
        return remote, repo, git(repo, "rev-parse", "HEAD")

    remote, repo, seen = fixture("holds")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")
    held = run_cli(push_branch, ["--force-with-lease=%s:%s" % (branch, seen)], env=env, cwd=repo)
    replaced = remote_at(remote, branch) == git(repo, "rev-parse", "HEAD")

    remote, repo, seen = fixture("stale")
    moved = git(repo, "commit-tree", "-p", seen, "-m", "someone else's push", seen + "^{tree}")
    git(repo, "push", "-q", "origin", "%s:refs/heads/%s" % (moved, branch))
    git(repo, "commit", "-q", "--amend", "-m", "rebased")
    stale = run_cli(push_branch, ["--force-with-lease=%s:%s" % (branch, seen)], env=env, cwd=repo)
    after_stale = remote_at(remote, branch)
    plain = run_cli(push_branch, [], env=env, cwd=repo)
    after_plain = remote_at(remote, branch)
    forced = run_cli(push_branch, ["--force"], env=env, cwd=repo)
    after_forced = remote_at(remote, branch)

    assert held[0] == 0 and replaced
    assert stale[0] == 1 and after_stale == moved
    assert plain[0] == 1 and after_plain == moved
    assert forced == (2, "", "push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, got '--force'\n"
                             "usage: push-branch.sh [--force-with-lease=<branch>:<sha>]\n")
    assert after_forced == moved


@pytest.mark.process("push-branch.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_from_another_directory_answers_as_in_place_recording_push_failed_in_that_directorys_events(
        tmp_path, run_cli, push_branch, events, monkeypatch):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    env = {**LANDED_ENV, "VERI_ISSUE": "720", "VERI_PUSH_RETRIES": "0"}
    in_place = run_repo(tmp_path / "in-place", tmp_path / "no-such-remote.git")
    linked = run_repo(tmp_path / "linked", tmp_path / "no-such-remote.git")

    expected = run_cli(push_branch, [], env=env, cwd=in_place)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "push-branch.sh")], cwd=linked,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == expected == (0, "", expected[2])
    assert [r["event"] for r in events.records(linked)] == ["stage-start", "push-failed", "stage-end"]


def test_a_bad_argument_and_a_bad_push_retries_each_exit_2_with_nothing_on_stdout_and_their_stderr_text(
        tmp_path, run_cli, push_branch):
    usage = "usage: push-branch.sh [--force-with-lease=<branch>:<sha>]\n"
    only = "push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, got '%s'\n"

    answers = {argv[0]: run_cli(push_branch, argv, env={"VERI_PUSH_BACKOFF": "0"}, cwd=tmp_path)
               for argv in (["--bogus"], ["--force-with-lease"], ["--force-with-lease=tdd/1-x"])}
    tunable = run_cli(push_branch, [], env={"VERI_PUSH_RETRIES": "x", "VERI_PUSH_BACKOFF": "0"}, cwd=tmp_path)

    assert answers == {arg: (2, "", only % arg + usage)
                       for arg in ("--bogus", "--force-with-lease", "--force-with-lease=tdd/1-x")}
    assert tunable == (2, "", "push-branch.sh: VERI_PUSH_RETRIES must be a non-negative integer, got 'x'\n")


@pytest.mark.process("git push --force-with-lease to a bare repository")
def test_no_argument_with_a_rebase_lease_file_pushes_a_rewritten_history_over_a_remote_still_at_the_leased_sha(
        tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "work", remote)
    git(repo, "push", "-q", "origin", BRANCH)
    (repo / ".tdd" / "rebase-lease").write_text(git(repo, "rev-parse", "HEAD") + "\n")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")

    code, _, _ = run_cli(push_branch, [], env={**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}, cwd=repo)

    assert (code, remote_at(remote)) == (0, git(repo, "rev-parse", "HEAD"))


@pytest.mark.process("git push --force-with-lease to a bare repository")
def test_a_push_under_the_rebase_lease_that_lands_removes_the_lease_file_so_the_next_push_is_plain(
        tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "work", remote)
    git(repo, "push", "-q", "origin", BRANCH)
    lease = repo / ".tdd" / "rebase-lease"
    lease.write_text(git(repo, "rev-parse", "HEAD") + "\n")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")

    code, _, _ = run_cli(push_branch, [], env={**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}, cwd=repo)

    assert (code, remote_at(remote), lease.exists()) == (0, git(repo, "rev-parse", "HEAD"), False)


@pytest.mark.process("git push --force-with-lease to a bare repository")
def test_force_with_lease_naming_a_sha_the_remote_never_had_pushes_under_the_sha_the_rebase_lease_records(
        tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "work", remote)
    git(repo, "push", "-q", "origin", BRANCH)
    (repo / ".tdd" / "rebase-lease").write_text(git(repo, "rev-parse", "HEAD") + "\n")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")
    never_had = git(repo, "commit-tree", "-m", "a later rebase's pre-rebase sha", "HEAD^{tree}")

    code, _, _ = run_cli(push_branch, ["--force-with-lease=%s:%s" % (BRANCH, never_had)],
                         env={**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}, cwd=repo)

    assert (code, remote_at(remote)) == (0, git(repo, "rev-parse", "HEAD"))


@pytest.mark.process("rebase-onto-default.sh then push-branch.sh against a bare repository")
def test_rebase_exiting_3_after_a_repair_step_leaves_the_lease_naming_the_pre_rebase_sha_and_the_push_replaces_the_remote_at_it(
        tmp_path, run_cli, push_branch):
    rebase = importlib.import_module("veri.rebase_onto_default")
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "work", remote)
    git(repo, "push", "-q", "origin", "main", BRANCH)
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-head", "origin", "main")
    pre = git(repo, "rev-parse", "HEAD")
    lease = repo / ".tdd" / "rebase-lease"
    lease.write_text(pre + "\n")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")
    (repo / "repair.txt").write_text("repair\n")
    git(repo, "add", "repair.txt")
    git(repo, "commit", "-q", "-m", "fix: the repair step's green commit (#191)")

    rebased = run_cli(rebase, [], cwd=repo)
    lease_after_rebase = lease.read_text().strip() if lease.exists() else "<absent>"
    pushed = run_cli(push_branch, [], env={**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}, cwd=repo)

    assert rebased[0] == 3 and lease_after_rebase == pre
    assert (pushed[0], remote_at(remote), lease.exists()) == (0, git(repo, "rev-parse", "HEAD"), False)


@pytest.mark.process("resume-clean.sh then push-branch.sh against a bare repository")
def test_a_resume_between_the_rebase_and_the_push_keeps_the_lease_and_the_push_replaces_the_remote_at_the_pre_rebase_sha(
        tmp_path, run_cli, push_branch):
    clean = importlib.import_module("veri.resume_clean")
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "work", remote)
    (repo / "tracked.txt").write_text("committed\n")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-q", "-m", "feat: a tracked file (#191)")
    git(repo, "push", "-q", "origin", BRANCH)
    pre = git(repo, "rev-parse", "HEAD")
    lease = repo / ".tdd" / "rebase-lease"
    lease.write_text(pre + "\n")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")
    (repo / "tracked.txt").write_text("uncommitted\n")

    resumed = run_cli(clean, [], cwd=repo)
    lease_after_resume = lease.read_text().strip() if lease.exists() else "<absent>"
    pushed = run_cli(push_branch, [], env={**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}, cwd=repo)

    assert (resumed[0], lease_after_resume) == (0, pre)
    assert (pushed[0], remote_at(remote), lease.exists()) == (0, git(repo, "rev-parse", "HEAD"), False)


@pytest.mark.process("git push --force-with-lease to an unreachable and then a reachable bare repository")
def test_a_failed_push_leaves_the_lease_so_the_next_push_with_origin_back_replaces_the_remote_at_the_leased_sha(
        tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = run_repo(tmp_path / "work", remote)
    git(repo, "push", "-q", "origin", BRANCH)
    pre = git(repo, "rev-parse", "HEAD")
    lease = repo / ".tdd" / "rebase-lease"
    lease.write_text(pre + "\n")
    git(repo, "commit", "-q", "--amend", "-m", "rebased")
    env = {**LANDED_ENV, "VERI_PUSH_RETRIES": "0"}

    git(repo, "remote", "set-url", "origin", str(tmp_path / "no-such-remote.git"))
    failed = run_cli(push_branch, [], env=env, cwd=repo)
    lease_after_failure = lease.read_text().strip() if lease.exists() else "<absent>"
    remote_after_failure = remote_at(remote)
    git(repo, "remote", "set-url", "origin", str(remote))
    pushed = run_cli(push_branch, [], env=env, cwd=repo)

    assert (failed[0], lease_after_failure, remote_after_failure) == (0, pre, pre)
    assert (pushed[0], remote_at(remote), lease.exists()) == (0, git(repo, "rev-parse", "HEAD"), False)

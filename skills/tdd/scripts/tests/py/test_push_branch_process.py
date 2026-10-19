"""Cases for push-branch.sh, driven through its command-line interface."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS

BRANCH = "tdd/191-run-commits-live-on-one-disk"
SHA = "a" * 40
LANDED_ENV = {"VERI_ISSUE": "191", "VERI_ACTOR": "conductor", "VERI_PUSH_BACKOFF": "0", "VERI_STEP": "a step"}


@pytest.fixture
def push_branch():
    return importlib.import_module("veri.push_branch")


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def fixture_repo(path, remote=None, branch=BRANCH):
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    git(path, "commit", "-q", "--allow-empty", "-m", "initial")
    git(path, "checkout", "-q", "-b", branch)
    (path / ".tdd").mkdir()
    (path / ".tdd" / "issue-191.md").write_text("\n- [x] a step ⟂ refactor pending\n- [ ] the next step\n")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "feat: a step's green commit (#191)")
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
    repo = fixture_repo(tmp_path / "run", tmp_path / "no-such-remote.git")
    ledger = repo / ".tdd" / "issue-191.md"
    before = (git(repo, "rev-parse", "HEAD"), git(repo, "rev-list", "--count", "HEAD"), ledger.read_text())

    code, out, err = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    assert code == 0
    assert (git(repo, "rev-parse", "HEAD"), git(repo, "rev-list", "--count", "HEAD"), ledger.read_text()) == before
    assert [(r["event"], r["attempts"]) for r in events.records(repo)] == [("push-failed", "4")]


@pytest.mark.process("git push to a bare repository")
def test_a_push_that_lands_leaves_the_branch_on_the_remote_at_the_commit_head_is_on(tmp_path, run_cli, push_branch):
    remote = bare(tmp_path / "origin.git")
    repo = fixture_repo(tmp_path / "landed", remote)

    code, out, err = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    assert code == 0
    assert remote_at(remote) == git(repo, "rev-parse", "HEAD")


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
    assert [(r["event"], r["remote_sha"]) for r in events.records(tmp_path)] == [("push-rejected", SHA)]


@pytest.mark.process("git push to a bare repository")
def test_a_push_that_lands_exits_0_writes_nothing_to_stderr_and_appends_no_event(
        tmp_path, run_cli, push_branch, events):
    remote = bare(tmp_path / "origin.git")
    repo = fixture_repo(tmp_path / "quiet", remote)

    code, out, err = run_cli(push_branch, [], env=LANDED_ENV, cwd=repo)

    assert (code, out, err) == (0, "", "")
    assert events.records(repo) == []


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
        repo = fixture_repo(tmp_path / name, remote, branch)
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
    in_place = fixture_repo(tmp_path / "in-place", tmp_path / "no-such-remote.git")
    linked = fixture_repo(tmp_path / "linked", tmp_path / "no-such-remote.git")

    expected = run_cli(push_branch, [], env=env, cwd=in_place)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    ran = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "push-branch.sh")], cwd=linked,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == expected == (0, "", expected[2])
    assert [r["event"] for r in events.records(linked)] == ["push-failed"]


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

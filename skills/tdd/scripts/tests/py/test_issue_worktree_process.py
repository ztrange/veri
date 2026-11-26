"""Process cases split from test_issue_worktree.py: they start a real process or put a local fake in front of one."""
import collections.abc
import importlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import pytest


@pytest.fixture(autouse=True)
def case_works_in_its_scratch_tree(tmp_path, monkeypatch):
    """issue_worktree.py runs git with no cwd; from the case's own tmp_path the git guard sees every call."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def issue_worktree():
    return importlib.import_module("veri.issue_worktree")


class Argvs(collections.abc.Sequence):
    """The argv lists a fake_processes fake has recorded so far, read live: a helper hands one back before the code runs."""

    def __init__(self, fake):
        self.fake = fake

    def __len__(self):
        return len(self.fake.seen)

    def __getitem__(self, index):
        return self.fake.argvs[index]

    def __eq__(self, other):
        return self.fake.argvs == other


def routing_git(fake_processes, answers):
    """fake_processes answering each git argv tuple in <answers> with (exit code, stdout, stderr), each stream sent where the call routes it."""
    table = {" ".join(argv): answer for argv, answer in answers.items()}

    def deliver(text, target):
        if target in (subprocess.PIPE, subprocess.DEVNULL):
            return
        if target is None:
            sys.stdout.write(text)
        elif target == 1:
            sys.stdout.write(text)
        elif target == 2 or target == subprocess.STDOUT:
            sys.stderr.write(text)
        else:
            target.write(text)

    def answer(line, **kwargs):
        if line not in table and line.startswith("git for-each-ref "):
            return (0, "", "")
        if line not in table:
            raise AssertionError("unexpected command: %r" % (line,))
        code, stdout, stderr = table[line]
        captured = kwargs.get("capture_output")
        out_to = subprocess.PIPE if captured else kwargs.get("stdout")
        err_to = subprocess.PIPE if captured else kwargs.get("stderr")
        deliver(stdout, out_to)
        deliver(stderr, 2 if err_to is None else err_to)
        return (code, stdout if out_to == subprocess.PIPE else None, stderr if err_to == subprocess.PIPE else None)

    return Argvs(fake_processes.answers({}, default=answer))


@pytest.mark.process("a stand-in conductor (a claude under run_conductor.py) left running beside real git worktree calls")
def test_main_hands_back_a_registered_worktree_by_n_alone_unless_its_pid_file_names_a_live_conductor(fake_processes, 
        monkeypatch, capfd, tmp_path, issue_worktree, run_cli):
    import os

    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/7"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree %s\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/7-slug\n\n"
                % (main_tree, path))
    listing = ("git", "worktree", "list", "--porcelain")
    live = {0, 4242}

    def fake_kill(pid, sig):
        if pid > 2 ** 63:
            raise OverflowError("signed integer is greater than maximum")
        if pid == 1:
            raise PermissionError(1, "Operation not permitted")
        if pid not in live:
            raise ProcessLookupError(3, "No such process")

    monkeypatch.setattr(os, "kill", fake_kill)

    for slug in ("slug", "other"):
        calls = routing_git(fake_processes, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", slug])
        assert (slug, code, capfd.readouterr()[:], calls) == (slug, 0, (path + "\n", ""), [list(listing)])

    pid_file = pathlib.Path(path) / ".tdd" / "conductor.pid"
    pid_file.parent.mkdir(parents=True)
    for content in ("4242\r\n", "pid 4242\n", "-4242\n", "1\n", "999\n", "99999999999999999999\n", "", "\n", "0\n"):
        pid_file.write_text(content)
        calls = routing_git(fake_processes, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", "slug"])
        assert (content, code, capfd.readouterr()[:], calls) == (content, 0, (path + "\n", ""), [list(listing)])

    monkeypatch.undo()
    import time

    repo = scratch_repo(tmp_path / "held")
    want = scratch_wt_path(repo, 13)
    assert run_cli(issue_worktree, ["13", "own-run"], cwd=repo)[0] == 0
    real_pid_file = pathlib.Path(want, ".tdd", "conductor.pid")
    real_pid_file.parent.mkdir(parents=True, exist_ok=True)

    real_pid_file.write_text("%d\n" % os.getppid())
    own = run_cli(issue_worktree, ["13", "own-run"], cwd=repo)

    claude_pid = tmp_path / "claude.pid"
    claude = tmp_path / "claude"
    claude.write_text('#!/bin/sh\necho $$ > "%s"\nsleep 30\n' % claude_pid)
    launcher = tmp_path / "run_conductor.py"
    launcher.write_text('#!/bin/sh\n"%s" -p run\n' % claude)
    for stub in (claude, launcher):
        stub.chmod(0o755)
    parent = subprocess.Popen([str(launcher), "13"])
    try:
        for _ in range(200):
            if claude_pid.exists() and claude_pid.read_text().strip():
                break
            time.sleep(0.05)
        holder = claude_pid.read_text().strip()
        real_pid_file.write_text(holder + "\n")
        other = run_cli(issue_worktree, ["13", "own-run"], cwd=repo)
    finally:
        if claude_pid.exists() and claude_pid.read_text().strip():
            os.kill(int(claude_pid.read_text()), 15)
        parent.terminate()
        parent.wait()

    assert (own[0], own[1].strip(), other[0], other[1], holder in other[2]) == (0, want, 2, "", True)


def test_main_puts_a_seeded_log_back_when_the_cut_dies_and_still_maps_the_dying_add_into_0_to_3(fake_processes, 
        monkeypatch, capsys, tmp_path, issue_worktree):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/63"
    seeded = pathlib.Path(path, ".tdd", "events.jsonl")
    seeded.parent.mkdir(parents=True)
    seeded.write_bytes(b'{"event":"seeded"}\n{"event":"second"}\n')
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr(tempfile, "tempdir", None)
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/63-own-trap"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/63-own-trap"): (1, "", ""),
        ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"): (1, "", ""),
        ("git", "remote", "get-url", "origin"): (2, "", "error: No such remote 'origin'\n"),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/main"): (0, "", ""),
        ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/63-own-trap", path, "main"): (5, "", ""),
    })
    routed = subprocess.run
    path_at_add = []

    def run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "add"]:
            path_at_add.append(sorted(str(p.relative_to(path)) for p in pathlib.Path(path).rglob("*"))
                               if os.path.exists(path) else None)
        return routed(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)

    code = issue_worktree.main(["63", "own-trap"])

    assert (code, capsys.readouterr().out, path_at_add, seeded.read_bytes(), sorted(tmpdir.rglob("*"))) == (
        2, "", [None], b'{"event":"seeded"}\n{"event":"second"}\n', [])


@pytest.mark.parametrize("extra", ["notes.txt", ".tdd/.lock"])
def test_main_leaves_a_path_holding_more_than_the_seeded_log_where_it_is_for_git_to_refuse(fake_processes, 
        monkeypatch, capsys, tmp_path, issue_worktree, extra):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/63"
    seeded = pathlib.Path(path, ".tdd", "events.jsonl")
    seeded.parent.mkdir(parents=True)
    seeded.write_bytes(b'{"event":"seeded"}\n')
    pathlib.Path(path, extra).write_bytes(b"x\n")
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr(tempfile, "tempdir", None)
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/63-own-trap"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/63-own-trap"): (1, "", ""),
        ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"): (1, "", ""),
        ("git", "remote", "get-url", "origin"): (2, "", "error: No such remote 'origin'\n"),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/main"): (0, "", ""),
        ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/63-own-trap", path, "main"): (
            128, "", "fatal: '%s' already exists\n" % path),
    })
    routed = subprocess.run
    path_at_add = []

    def run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "add"]:
            path_at_add.append(sorted(str(p.relative_to(path)) for p in pathlib.Path(path).rglob("*")))
        return routed(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)

    code = issue_worktree.main(["63", "own-trap"])

    assert (code, capsys.readouterr().out, path_at_add, seeded.read_bytes(), sorted(tmpdir.rglob("*"))) == (
        2, "", [sorted([".tdd", ".tdd/events.jsonl", extra])], b'{"event":"seeded"}\n', [])


def test_main_appends_a_seeded_log_into_the_tdd_directory_a_successful_cut_checked_out(fake_processes, 
        monkeypatch, capsys, tmp_path, issue_worktree):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/63"
    seeded = pathlib.Path(path, ".tdd", "events.jsonl")
    seeded.parent.mkdir(parents=True)
    seeded.write_bytes(b'{"event":"seeded"}\n')
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr(tempfile, "tempdir", None)
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/63-own-trap"): (0, "", ""),
        ("git", "worktree", "add", "-q", path, "tdd/63-own-trap"): (0, "", ""),
    })
    routed = subprocess.run

    def run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "add"]:
            pathlib.Path(path, ".tdd").mkdir(parents=True)
            pathlib.Path(path, ".tdd", "events.jsonl").write_bytes(b'{"event":"committed"}\n')
        return routed(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)

    code = issue_worktree.main(["63", "own-trap"])

    assert (code, capsys.readouterr().out, seeded.read_bytes(), sorted(tmpdir.rglob("*"))) == (
        0, path + "\n", b'{"event":"committed"}\n{"event":"seeded"}\n', [])


def test_main_restores_a_seeded_log_after_a_successful_cut_without_issue_worktree_opening_events_jsonl_itself(fake_processes, 
        monkeypatch, capsys, tmp_path, issue_worktree):
    import builtins

    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/63"
    seeded = pathlib.Path(path, ".tdd", "events.jsonl")
    seeded.parent.mkdir(parents=True)
    seeded.write_bytes(b'{"event":"seeded"}\n')
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr(tempfile, "tempdir", None)
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/63-own-trap"): (0, "", ""),
        ("git", "worktree", "add", "-q", path, "tdd/63-own-trap"): (0, "", ""),
    })
    routed = subprocess.run

    def run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "add"]:
            pathlib.Path(path, ".tdd").mkdir(parents=True)
            pathlib.Path(path, ".tdd", "events.jsonl").write_bytes(b'{"event":"committed"}\n')
        return routed(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)
    opened = []

    def spy_open(file, *args, **kwargs):
        opened.append(str(file))
        return builtins.open(file, *args, **kwargs)

    monkeypatch.setattr(issue_worktree, "open", spy_open, raising=False)

    code = issue_worktree.main(["63", "own-trap"])

    assert (code, capsys.readouterr().out, seeded.read_bytes(), sorted(tmpdir.rglob("*"))) == (
        0, path + "\n", b'{"event":"committed"}\n{"event":"seeded"}\n', [])
    assert [p for p in opened if p.endswith("events.jsonl")] == []


def test_main_puts_a_seeded_log_back_when_it_refuses_for_the_origin_default_the_missing_default_or_the_failed_fetch(fake_processes, 
        monkeypatch, capsys, tmp_path, issue_worktree):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/63"
    seeded = pathlib.Path(path, ".tdd", "events.jsonl")
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr(tempfile, "tempdir", None)
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    get_url = ("git", "remote", "get-url", "origin")
    ls_remote = ("git", "ls-remote", "--symref", "origin", "HEAD")
    fetch = ("git", "fetch", "-q", "origin", "trunk")
    base = {
        ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/63-*"): (0, "", ""),
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/63-own-trap"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/63-own-trap"): (1, "", ""),
    }
    refusals = (
        ("origin default", ls_remote,
         {symref: (1, "", ""), get_url: (0, "/srv/origin.git\n", ""), ls_remote: (128, "", "")},
         "issue-worktree: cannot determine origin's default branch"
         " (no refs/remotes/origin/HEAD, and the remote did not name one)\n"),
        ("no origin", ("git", "show-ref", "--verify", "--quiet", "refs/heads/master"),
         {symref: (1, "", ""), get_url: (2, "", ""),
          ("git", "show-ref", "--verify", "--quiet", "refs/heads/main"): (1, "", ""),
          ("git", "show-ref", "--verify", "--quiet", "refs/heads/master"): (1, "", "")},
         "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)\n"),
        ("fetch", fetch,
         {symref: (0, "origin/trunk\n", ""), get_url: (0, "/srv/origin.git\n", ""),
          fetch: (1, "", "fatal: couldn't find remote ref trunk\n")},
         "issue-worktree: git fetch origin trunk failed — refusing to cut tdd/63-own-trap from a stale origin/trunk\n"),
    )
    for label, refusing, answers, refusal in refusals:
        seeded.parent.mkdir(parents=True)
        seeded.write_bytes(b'{"event":"seeded"}\n{"event":"second"}\n')
        routing_git(fake_processes, {**base, **answers})
        routed = subprocess.run
        path_at_refusal = []

        def run(args, *, refusing=refusing, path_at_refusal=path_at_refusal, routed=routed, **kwargs):
            if tuple(args) == refusing:
                path_at_refusal.append(os.path.exists(path))
            return routed(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", run)

        code = issue_worktree.main(["63", "own-trap"])

        out, err = capsys.readouterr()
        assert (label, code, out, err.endswith(refusal), path_at_refusal,
                seeded.read_bytes() if seeded.exists() else None, sorted(tmpdir.rglob("*"))) == (
            label, 2, "", True, [False], b'{"event":"seeded"}\n{"event":"second"}\n', [])
        seeded.unlink()
        seeded.parent.rmdir()
        pathlib.Path(path).rmdir()


def scratch_git(repo, *args):
    """Real git in <repo> under a fixed identity; its stdout, stripped."""
    done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True)
    return done.stdout.strip()


def scratch_repo(path):
    path.mkdir(parents=True)
    scratch_git(path, "init", "-q", "-b", "main")
    scratch_git(path, "commit", "-q", "--allow-empty", "-m", "initial")
    return path.resolve()


def scratch_wt_path(repo, n):
    return "%s/.tdd/wt/%s" % (repo.resolve(), n)


def scratch_registry(repo):
    return (scratch_git(repo, "worktree", "list", "--porcelain"),
            scratch_git(repo, "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads"))


def scratch_linked(repo, name, branch):
    path = repo.parent.resolve() / name
    scratch_git(repo, "worktree", "add", "-q", "-b", branch, str(path), "main")
    return path


@pytest.mark.process("git worktree add on a scratch repository, read back with git rev-parse")
def test_fresh_call_creates_a_worktree_at_dot_tdd_wt_7_on_a_new_branch_off_the_default_branch_and_prints_its_path(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "fresh")
    main_tip = scratch_git(repo, "rev-parse", "main")
    scratch_git(repo, "switch", "-q", "-c", "side")
    scratch_git(repo, "commit", "-q", "--allow-empty", "-m", "work on side")
    want = scratch_wt_path(repo, 7)

    code, out, _ = run_cli(issue_worktree, ["7", "add-worktree"], cwd=repo)

    assert (code, out.strip(), scratch_git(want, "rev-parse", "--show-toplevel"),
            scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD")) == (
        0, want, want, "tdd/7-add-worktree", main_tip)


@pytest.mark.process("git worktree add on a scratch repository whose path holds the run state a conductor seeds")
def test_fresh_cut_leaves_no_handed_back_marker_with_the_path_alone_on_stdout_issue_2460(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "unmarked")
    want = scratch_wt_path(repo, 12)
    state = pathlib.Path(want, ".tdd")
    state.mkdir(parents=True)
    (state / "events.jsonl").write_bytes(b'{"event":"seeded"}\n')
    (state / "conductor.pid").write_bytes(b"4242\n")

    code, out, err = run_cli(issue_worktree, ["12", "unmarked"], cwd=repo)

    assert (code, out, err, sorted(p.name for p in state.iterdir())) == (
        0, want + "\n", "", ["conductor.pid", "events.jsonl"])


@pytest.mark.process("git worktree add on a scratch repository whose path holds the run state a conductor seeds")
def test_fresh_call_cuts_the_worktree_and_keeps_the_seeded_events_and_conductor_pid_issue_2249(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "seeded")
    want = scratch_wt_path(repo, 11)
    state = pathlib.Path(want, ".tdd")
    state.mkdir(parents=True)
    (state / "events.jsonl").write_bytes(b'{"event":"seeded"}\n')
    (state / "conductor.pid").write_bytes(b"4242\n")

    code, out, _ = run_cli(issue_worktree, ["11", "seeded-state"], cwd=repo)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"),
            (state / "events.jsonl").read_bytes(), (state / "conductor.pid").read_bytes()) == (
        0, want, "tdd/11-seeded-state", b'{"event":"seeded"}\n', b"4242\n")


@pytest.mark.process("git worktree add twice on a scratch repository, its registry read back")
def test_second_call_prints_the_same_path_exits_0_and_creates_nothing_new(tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "again")
    want = scratch_wt_path(repo, 9)

    first = run_cli(issue_worktree, ["9", "resume-me"], cwd=repo)
    before = scratch_registry(repo)
    second = run_cli(issue_worktree, ["9", "resume-me"], cwd=repo)

    assert (first[0], second[0], second[1].strip(), first[1], scratch_registry(repo)) == (
        0, 0, want, second[1], before)


@pytest.mark.process("git worktree add on a scratch repository whose branch another worktree holds")
def test_branch_checked_out_elsewhere_exits_2_naming_that_worktree_and_touches_nothing(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "taken")
    other = scratch_linked(repo, "taken-elsewhere", "tdd/11-collide")
    mine = scratch_wt_path(repo, 11)
    before = scratch_registry(repo)

    code, out, err = run_cli(issue_worktree, ["11", "collide"], cwd=repo)

    assert (code, out, str(other) in err, os.path.exists(mine), scratch_registry(repo)) == (2, "", True, False, before)


@pytest.mark.process("git worktree remove on scratch repositories, a clean worktree and one with a staged file")
def test_remove_removes_a_clean_worktree_and_refuses_one_with_uncommitted_changes_with_exit_2(
        tmp_path, issue_worktree, run_cli):
    clean = scratch_repo(tmp_path / "remove-clean")
    want = scratch_wt_path(clean, 13)
    run_cli(issue_worktree, ["13", "done-with-this"], cwd=clean)

    clean_code = run_cli(issue_worktree, ["--remove", "13"], cwd=clean)[0]

    assert (clean_code, "worktree %s" % want in scratch_registry(clean)[0], os.path.exists(want)) == (0, False, False)

    dirty = scratch_repo(tmp_path / "remove-dirty")
    held = scratch_wt_path(dirty, 14)
    run_cli(issue_worktree, ["14", "still-working"], cwd=dirty)
    pathlib.Path(held, "notes.txt").write_text("work in progress\n")
    scratch_git(held, "add", "notes.txt")
    before = scratch_registry(dirty)

    dirty_code = run_cli(issue_worktree, ["--remove", "14"], cwd=dirty)[0]

    assert (dirty_code, os.path.exists(os.path.join(held, "notes.txt")), scratch_registry(dirty)) == (2, True, before)


@pytest.mark.process("git worktree remove on a scratch repository whose worktree holds a pinned scripts copy")
def test_remove_of_a_clean_worktree_holding_the_pinned_scripts_copy_succeeds_and_the_copy_goes_with_it_issue_2627(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "remove-pinned")
    held = scratch_wt_path(repo, 2627)
    run_cli(issue_worktree, ["2627", "pinned-copy"], cwd=repo)
    kept = pathlib.Path(held, ".tdd", "pinned-scripts")
    kept.mkdir(parents=True)
    (kept / "status.sh").write_text("#!/bin/sh\n")
    (kept / ".gitignore").write_text("*\n")

    code = run_cli(issue_worktree, ["--remove", "2627"], cwd=repo)[0]

    assert (code, os.path.exists(kept), os.path.exists(held)) == (0, False, False)


@pytest.mark.process("git worktree add on a scratch repository holding the branch already")
def test_existing_branch_no_worktree_checks_the_branch_out_into_dot_tdd_wt_17_instead_of_failing_on_dash_b(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "existing-branch")
    scratch_git(repo, "switch", "-q", "-c", "tdd/17-resume")
    scratch_git(repo, "commit", "-q", "--allow-empty", "-m", "work from the previous run")
    branch_tip = scratch_git(repo, "rev-parse", "tdd/17-resume")
    scratch_git(repo, "switch", "-q", "main")
    want = scratch_wt_path(repo, 17)

    code, out, _ = run_cli(issue_worktree, ["17", "resume"], cwd=repo)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD")) == (
        0, want, "tdd/17-resume", branch_tip)


@pytest.mark.process("git clone and git worktree add on scratch repositories, origin/HEAD naming trunk")
def test_origin_head_names_a_default_branch_that_is_neither_main_nor_master_cuts_the_new_worktree_from_it(
        tmp_path, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "upstream-trunk")
    scratch_git(upstream, "branch", "-m", "main", "trunk")
    clone = tmp_path / "clone-trunk"
    subprocess.run(["git", "clone", "-q", str(upstream), str(clone)], capture_output=True)
    scratch_git(clone, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    trunk_tip = scratch_git(clone, "rev-parse", "refs/remotes/origin/trunk")
    want = scratch_wt_path(clone, 21)

    code = run_cli(issue_worktree, ["21", "remote-default"], cwd=clone)[0]

    assert (code, scratch_git(want, "rev-parse", "HEAD")) == (0, trunk_tip)


@pytest.mark.process("git worktree add on a scratch repository with only a local master")
def test_no_remote_and_only_a_local_master_cuts_tdd_23_local_master_from_master(tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "local-master")
    scratch_git(repo, "branch", "-m", "main", "master")
    master_tip = scratch_git(repo, "rev-parse", "master")
    scratch_git(repo, "switch", "-q", "-c", "side")
    scratch_git(repo, "commit", "-q", "--allow-empty", "-m", "work on side")
    want = scratch_wt_path(repo, 23)

    code, out, _ = run_cli(issue_worktree, ["23", "local-master"], cwd=repo)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD")) == (
        0, want, "tdd/23-local-master", master_tip)


@pytest.mark.process("git worktree list on a scratch repository with neither main nor master")
def test_no_remote_and_no_main_or_master_exits_2_with_a_diagnostic_on_stderr_nothing_on_stdout_and_nothing_created(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "no-default")
    scratch_git(repo, "branch", "-m", "main", "trunk")
    before = scratch_registry(repo)

    code, out, err = run_cli(issue_worktree, ["25", "no-default"], cwd=repo)

    assert (code, out, "default branch" in err, scratch_registry(repo)) == (2, "", True, before)


@pytest.mark.process("git worktree add from a linked worktree of a scratch repository")
def test_called_from_a_linked_worktree_creates_and_prints_the_main_working_trees_dot_tdd_wt_27_not_one_nested_inside_the_caller(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "from-linked")
    linked = scratch_linked(repo, "from-linked-session", "session")
    want = scratch_wt_path(repo, 27)

    code, out, _ = run_cli(issue_worktree, ["27", "from-linked"], cwd=linked)

    assert (code, out.strip(), scratch_git(want, "rev-parse", "--show-toplevel"),
            os.path.exists(scratch_wt_path(linked, 27))) == (0, want, want, False)


def scratch_clone(tmp_path, name):
    upstream = scratch_repo(tmp_path / (name + "-upstream"))
    clone = tmp_path / (name + "-clone")
    subprocess.run(["git", "clone", "-q", str(upstream), str(clone)], capture_output=True)
    return upstream, clone


@pytest.mark.process("git worktree add from a linked worktree, then again from the main working tree")
def test_created_from_a_linked_worktree_called_again_from_the_main_working_tree_prints_the_same_path_and_creates_nothing(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "cross-caller")
    linked = scratch_linked(repo, "cross-caller-session", "cross-session")
    want = scratch_wt_path(repo, 29)

    first = run_cli(issue_worktree, ["29", "cross-caller"], cwd=linked)
    before = scratch_registry(repo)
    second = run_cli(issue_worktree, ["29", "cross-caller"], cwd=repo)

    assert (first[0], second[0], second[1].strip(), second[1], scratch_registry(repo)) == (
        0, 0, want, first[1], before)


@pytest.mark.process("git worktree remove from a linked worktree of a scratch repository")
def test_remove_from_a_linked_worktree_removes_the_main_working_trees_dot_tdd_wt_31(tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "remove-from-linked")
    want = scratch_wt_path(repo, 31)
    run_cli(issue_worktree, ["31", "remove-from-linked"], cwd=repo)
    linked = scratch_linked(repo, "remove-from-linked-session", "remove-session")

    code = run_cli(issue_worktree, ["--remove", "31"], cwd=linked)[0]

    assert (code, "worktree %s" % want in scratch_registry(repo)[0], os.path.exists(want)) == (0, False, False)


@pytest.mark.process("git worktree add through a symlinked path to a scratch repository, its registry read back")
def test_reached_through_a_symlinked_path_prints_the_resolved_path_git_itself_lists_for_the_worktree(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "symlinked")
    via = tmp_path / "reached-by-symlink"
    via.symlink_to(repo)
    want = scratch_wt_path(repo, 33)

    code, out, _ = run_cli(issue_worktree, ["33", "through-symlink"], env={"PWD": str(via)}, cwd=via)

    assert (code, out.strip(), "worktree %s" % out.strip() in scratch_registry(repo)[0].split("\n")) == (0, want, True)


@pytest.mark.process("git clone and git worktree add on scratch repositories, origin ahead of the clone")
def test_origins_default_branch_is_ahead_of_the_local_one_cuts_tdd_35_from_remote_tip_from_origins_tip(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "ahead")
    scratch_git(upstream, "commit", "-q", "--allow-empty", "-m", "landed while the clone was busy")
    remote_tip = scratch_git(upstream, "rev-parse", "main")
    want = scratch_wt_path(clone, 35)

    code, out, _ = run_cli(issue_worktree, ["35", "from-remote-tip"], cwd=clone)

    assert (code, out.strip(), scratch_git(want, "rev-parse", "HEAD")) == (0, want, remote_tip)


@pytest.mark.process("git clone and git worktree add on scratch repositories, the clone's refs and tree read back")
def test_creating_the_issue_branch_leaves_the_local_default_branch_ref_and_the_callers_working_tree_untouched(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "untouched")
    (upstream / "landed.txt").write_text("landed while the clone was busy\n")
    scratch_git(upstream, "add", "landed.txt")
    scratch_git(upstream, "commit", "-q", "-m", "landed while the clone was busy")
    def seen():
        return (scratch_git(clone, "rev-parse", "refs/heads/main"), scratch_git(clone, "rev-parse", "HEAD"),
                scratch_git(clone, "branch", "--show-current"),
                scratch_git(clone, "status", "--porcelain", "--untracked-files=no"),
                (clone / "landed.txt").exists())
    before = seen()

    code = run_cli(issue_worktree, ["37", "leave-the-clone-alone"], cwd=clone)[0]

    assert (code, seen()) == (0, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, the new branch's upstream read back")
def test_the_new_issue_branch_has_no_upstream(tmp_path, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "no-tracking")
    want = scratch_wt_path(clone, 39)

    code, out, _ = run_cli(issue_worktree, ["39", "no-upstream"], cwd=clone)

    assert (code, out.strip(), scratch_git(clone, "for-each-ref", "--format=%(upstream:short)",
                                           "refs/heads/tdd/39-no-upstream")) == (0, want, "")


@pytest.mark.process("git worktree list on a scratch clone whose git fetch fails")
def test_the_fetch_fails_exits_2_with_a_diagnostic_on_stderr_nothing_on_stdout_and_no_worktree_or_branch_created(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "unreachable")
    want = scratch_wt_path(clone, 41)
    before = scratch_registry(clone)
    real_run = subprocess.run

    def run(args, **kwargs):
        if list(args)[:2] == ["git", "fetch"]:
            sys.stderr.write("fatal: unable to access remote\n")
            return subprocess.CompletedProcess(args, 128)
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(issue_worktree, ["41", "fetch-fails"], cwd=clone)

    assert (code, out, "fetch" in err, os.path.exists(want), scratch_registry(clone)) == (2, "", True, False, before)


@pytest.mark.process("git worktree add on a scratch repository with no remote, the new worktree read back")
def test_no_remote_at_all_cuts_tdd_43_no_remote_from_the_local_main_without_going_to_a_remote(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "no-remote")
    main_tip = scratch_git(repo, "rev-parse", "main")
    scratch_git(repo, "switch", "-q", "-c", "side")
    scratch_git(repo, "commit", "-q", "--allow-empty", "-m", "work on side")
    want = scratch_wt_path(repo, 43)

    code, out, err = run_cli(issue_worktree, ["43", "no-remote"], cwd=repo)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD"),
            err) == (0, want, "tdd/43-no-remote", main_tip, "")


@pytest.mark.process("git worktree add on a scratch clone whose origin is gone, the existing branch checked out")
def test_resume_onto_an_existing_issue_branch_with_the_remote_unreachable_checks_it_out_as_it_is(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "resume-no-fetch")
    scratch_git(clone, "switch", "-q", "-c", "tdd/45-resume-no-fetch")
    scratch_git(clone, "commit", "-q", "--allow-empty", "-m", "work from the previous run")
    branch_tip = scratch_git(clone, "rev-parse", "tdd/45-resume-no-fetch")
    scratch_git(clone, "switch", "-q", "main")
    shutil.rmtree(upstream)
    want = scratch_wt_path(clone, 45)

    code, out, err = run_cli(issue_worktree, ["45", "resume-no-fetch"], cwd=clone)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD"),
            err) == (0, want, "tdd/45-resume-no-fetch", branch_tip, "")


@pytest.mark.process("git clone and git worktree add on scratch repositories, origin/HEAD removed from the clone")
def test_origin_remote_without_origin_head_cuts_tdd_47_no_origin_head_from_the_freshly_fetched_tip(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "no-origin-head")
    scratch_git(upstream, "commit", "-q", "--allow-empty", "-m", "landed while the clone was busy")
    remote_tip = scratch_git(upstream, "rev-parse", "main")
    scratch_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    want = scratch_wt_path(clone, 47)

    code, out, _ = run_cli(issue_worktree, ["47", "no-origin-head"], cwd=clone)

    assert (scratch_git(clone, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"), code, out.strip(),
            scratch_git(want, "rev-parse", "HEAD")) == ("", 0, want, remote_tip)


@pytest.mark.process("git clone and git worktree add on scratch repositories, the remote's default a develop branch")
def test_origin_whose_default_is_develop_with_a_local_main_and_no_origin_head_cuts_tdd_865_from_develop_not_main(
        tmp_path, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "develop-upstream")
    main_only_tip = scratch_git(upstream, "rev-parse", "main")
    scratch_git(upstream, "switch", "-q", "-c", "develop")
    scratch_git(upstream, "commit", "-q", "--allow-empty", "-m", "work on the default branch")
    develop_tip = scratch_git(upstream, "rev-parse", "develop")
    clone = tmp_path / "develop-clone"
    subprocess.run(["git", "clone", "-q", str(upstream), str(clone)], capture_output=True)
    scratch_git(clone, "branch", "main", "refs/remotes/origin/main")
    scratch_git(clone, "config", "remote.origin.followRemoteHEAD", "never")
    scratch_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    want = scratch_wt_path(clone, 865)

    code, out, err = run_cli(issue_worktree, ["865", "develop-default"], cwd=clone)

    assert (scratch_git(clone, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"),
            scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/heads/main"), code, out.strip(),
            scratch_git(want, "rev-parse", "HEAD")) == ("", main_only_tip, 0, want, develop_tip)
    assert err == ""


@pytest.mark.process("git worktree list on a scratch clone whose origin is gone and records no origin/HEAD")
def test_origin_whose_default_cannot_be_resolved_and_no_origin_head_exits_2_naming_origin_head_and_creates_no_worktree(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    real_run = subprocess.run

    def silent_remote(args, **kwargs):
        if list(args[:2]) == ["git", "ls-remote"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if list(args[:2]) == ["git", "fetch"]:
            return subprocess.CompletedProcess(args, 128, "", "fatal: unable to access remote\n")
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", silent_remote)
    _, clone = scratch_clone(tmp_path, "unresolvable")
    scratch_git(clone, "config", "remote.origin.followRemoteHEAD", "never")
    scratch_git(clone, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    scratch_git(clone, "remote", "set-url", "origin", str(tmp_path / "unresolvable-gone"))
    want = scratch_wt_path(clone, 866)
    before = scratch_registry(clone)

    code, out, err = run_cli(issue_worktree, ["866", "unresolvable-default"], cwd=clone)

    assert (scratch_git(clone, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"), code, out,
            "refs/remotes/origin/HEAD" in err, os.path.exists(want), scratch_registry(clone) == before) == (
        "", 2, "", True, False, True)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a local branch one commit ahead of its remote")
def test_a_local_branch_ahead_of_its_remote_is_checked_out_at_its_own_tip_not_rewound_to_the_remotes(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "local-ahead")
    scratch_git(upstream, "switch", "-q", "-c", "tdd/53-local-ahead")
    scratch_git(upstream, "commit", "-q", "--allow-empty", "-m", "the tip the previous run pushed")
    remote_branch_tip = scratch_git(upstream, "rev-parse", "tdd/53-local-ahead")
    scratch_git(upstream, "switch", "-q", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    scratch_git(clone, "switch", "-q", "-c", "tdd/53-local-ahead", "origin/tdd/53-local-ahead")
    scratch_git(clone, "commit", "-q", "--allow-empty", "-m", "committed by the last run and never pushed")
    local_branch_tip = scratch_git(clone, "rev-parse", "tdd/53-local-ahead")
    scratch_git(clone, "switch", "-q", "main")
    want = scratch_wt_path(clone, 53)

    code, out, _ = run_cli(issue_worktree, ["53", "local-ahead"], cwd=clone)

    assert local_branch_tip != remote_branch_tip
    assert (scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/heads/tdd/53-local-ahead"),
            scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/tdd/53-local-ahead"),
            code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD")) == (
        local_branch_tip, remote_branch_tip, 0, want, "tdd/53-local-ahead", local_branch_tip)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a name in neither ref namespace")
def test_a_name_in_neither_namespace_in_a_repo_with_a_remote_is_still_cut_from_the_default_branch(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "neither")
    scratch_git(upstream, "switch", "-q", "-c", "tdd/99-some-other-run")
    scratch_git(upstream, "commit", "-q", "--allow-empty", "-m", "another issue's run, pushed")
    scratch_git(upstream, "switch", "-q", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    main_tip = scratch_git(clone, "rev-parse", "main")
    want = scratch_wt_path(clone, 55)
    assert scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/heads/tdd/55-neither") == ""

    code, out, _ = run_cli(issue_worktree, ["55", "neither"], cwd=clone)

    assert (scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/tdd/55-neither"),
            code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD")) == (
        "", 0, want, "tdd/55-neither", main_tip)


def answer_processes(monkeypatch, answer):
    """subprocess.run with <answer>(args) -> CompletedProcess|None in front of the real one: None lets the call through."""
    real_run = subprocess.run

    def run(args, **kwargs):
        got = answer(list(args))
        return got if got is not None else real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", run)


def ls_remote_gets_no_answer(monkeypatch):
    answer_processes(monkeypatch, lambda args: subprocess.CompletedProcess(args, 128, "", "")
                     if args[:2] == ["git", "ls-remote"] else None)


def commits(repo):
    return scratch_git(repo, "rev-list", "--all")


def prs_fixture(tmp_path, prs):
    gh = tmp_path / "gh"
    gh.mkdir()
    if prs is not None:
        (gh / "prs.json").write_text(json.dumps(prs) + "\n")
    return str(gh)


@pytest.mark.process("git clone and git worktree add on scratch repositories, ls-remote answering nothing")
def test_fresh_cut_whose_origin_ls_remote_gets_no_answer_exits_2_naming_the_ls_remote_lookup_and_creates_no_worktree_issue_1672(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "ls-remote-silent")
    want = scratch_wt_path(clone, 1672)
    before = scratch_registry(clone)
    ls_remote_gets_no_answer(monkeypatch)

    code, out, err = run_cli(issue_worktree, ["1672", "ls-remote-silent"], cwd=clone)

    assert (code, out, "ls-remote" in err, os.path.exists(want), scratch_registry(clone)) == (2, "", True, False, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, origin holding the issue's branch")
def test_issue_branch_already_on_the_remote_makes_a_fresh_call_exit_2_naming_that_remote_branch_and_leave_no_worktree_branch_or_commit_behind_issue_1656(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "remote-claimed")
    scratch_git(upstream, "branch", "-q", "tdd/61-someone-else", "main")
    want = scratch_wt_path(clone, 61)
    before = (scratch_registry(clone), commits(clone))

    code, _, err = run_cli(issue_worktree, ["61", "fresh-start"], cwd=clone)

    assert (code, "tdd/61-someone-else" in err, os.path.exists(want), (scratch_registry(clone), commits(clone))) == (
        2, True, False, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a PR fixture claiming the issue")
def test_open_pr_saying_closes_62_makes_a_fresh_call_exit_2_naming_that_pr_and_leave_no_worktree_branch_or_commit_behind_issue_1656(
        tmp_path, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "pr-claimed")
    want = scratch_wt_path(clone, 62)
    gh = prs_fixture(tmp_path, [{"body": "Closes #62", "isCrossRepository": False, "state": "OPEN", "isDraft": True,
                                 "url": "https://example.test/pull/620"}])
    before = (scratch_registry(clone), commits(clone))

    code, _, err = run_cli(issue_worktree, ["62", "fresh-start"], cwd=clone, env={"VERI_GH_JSON": gh})

    assert (code, "pull/620" in err, os.path.exists(want), (scratch_registry(clone), commits(clone))) == (
        2, True, False, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a fork's PR fixture saying it closes the issue")
def test_open_pr_from_a_fork_saying_closes_67_does_not_stop_a_fresh_call_issue_3974(tmp_path, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "fork-claimed")
    want = scratch_wt_path(clone, 67)
    gh = prs_fixture(tmp_path, [{"body": "Closes #67", "state": "OPEN", "isDraft": False, "isCrossRepository": True,
                                 "url": "https://example.test/pull/670"}])

    code, out, err = run_cli(issue_worktree, ["67", "fresh-start"], cwd=clone, env={"VERI_GH_JSON": gh})

    assert (code, out.strip(), os.path.exists(want)) == (0, want, True), err


@pytest.mark.process("git clone and git worktree add on scratch repositories, a PR fixture directory with no answer")
def test_fresh_cut_whose_open_pr_lookup_gets_no_answer_exits_2_naming_the_open_pr_lookup_and_creates_no_worktree_issue_1672(
        tmp_path, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "pr-silent")
    want = scratch_wt_path(clone, 64)
    before = scratch_registry(clone)

    code, out, err = run_cli(issue_worktree, ["64", "fresh-start"], cwd=clone,
                             env={"VERI_GH_JSON": prs_fixture(tmp_path, None)})

    assert (code, out, bool(re.search(r"open[- ]PR", err, re.I)), os.path.exists(want), scratch_registry(clone)) == (
        2, "", True, False, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a resume whose branch is on origin")
def test_resume_with_worktree_and_ledger_still_starts_though_its_branch_is_on_the_remote_and_an_open_pr_claims_the_issue_issue_1656(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "resume-claimed")
    scratch_git(upstream, "branch", "-q", "tdd/63-mine", "main")
    mine = scratch_wt_path(clone, 63)
    scratch_git(clone, "worktree", "add", "-q", "-b", "tdd/63-mine", mine, "main")
    pathlib.Path(mine, ".tdd").mkdir()
    pathlib.Path(mine, ".tdd", "issue-63.md").write_text("- [ ] step\n")
    gh = prs_fixture(tmp_path, [{"body": "Closes #63", "isCrossRepository": False, "state": "OPEN", "isDraft": True,
                                 "url": "https://example.test/pull/630"}])

    code, out, _ = run_cli(issue_worktree, ["63", "mine"], cwd=clone, env={"VERI_GH_JSON": gh})

    assert (code, out.strip()) == (0, mine)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a resume while ls-remote gets no answer")
def test_resume_of_the_runs_own_issue_branch_still_hands_back_its_worktree_when_the_ls_remote_and_open_pr_lookups_get_no_answer_issue_1672(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "resume-silent")
    mine = scratch_wt_path(clone, 65)
    scratch_git(clone, "worktree", "add", "-q", "-b", "tdd/65-mine", mine, "main")
    pathlib.Path(mine, ".tdd").mkdir()
    pathlib.Path(mine, ".tdd", "issue-65.md").write_text("- [ ] step\n")
    ls_remote_gets_no_answer(monkeypatch)

    code, out, _ = run_cli(issue_worktree, ["65", "mine"], cwd=clone,
                           env={"VERI_GH_JSON": prs_fixture(tmp_path, None)})

    assert (code, out.strip()) == (0, mine)


@pytest.mark.process("git clone on scratch repositories, a faked gh answering for a GitHub Enterprise origin")
def test_fresh_cut_from_a_github_enterprise_origin_runs_the_open_pr_check_and_an_open_pr_saying_closes_66_exits_2_naming_that_pr_and_creates_no_worktree_issue_1672(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    _, clone = scratch_clone(tmp_path, "ghe-claimed")
    want = scratch_wt_path(clone, 66)
    before = scratch_registry(clone)
    page = json.dumps([{"body": "Closes #66", "state": "OPEN", "head": {"repo": {"full_name": "acme/veri"}}, "base": {"repo": {"full_name": "acme/veri"}}, "url": "https://ghe.example.test/acme/veri/pull/660"}])

    def answer(args):
        if args[:4] == ["git", "remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(args, 0, "https://ghe.example.test/acme/veri.git\n", "")
        if args[0] == "gh":
            return subprocess.CompletedProcess(args, 0, page if re.search(r"[?&]page=1$", args[-1]) else "[]", "")
        return None

    answer_processes(monkeypatch, answer)
    monkeypatch.delenv("VERI_GH_JSON", raising=False)

    code, out, err = run_cli(issue_worktree, ["66", "fresh-start"], cwd=clone)

    assert (code, out, "pull/660" in err, os.path.exists(want), scratch_registry(clone)) == (2, "", True, False, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, a fetched remote-tracking ref of origin's branch")
def test_fresh_call_over_a_fetched_remote_tracking_ref_of_a_branch_origin_holds_exits_2_naming_the_branch_and_the_take_over_command_creating_no_worktree_or_branch_issue_1734(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "fetched-claimed")
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    scratch_git(upstream, "branch", "-q", "tdd/64-taken-over", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    want = scratch_wt_path(clone, 64)
    fetched = scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/tdd/64-taken-over")
    before = scratch_registry(clone)

    code, _, err = run_cli(issue_worktree, ["64", "taken-over"], cwd=clone)

    assert (bool(fetched), code, "issue-worktree.sh --take-over 64 taken-over" in err,
            os.path.exists(want), scratch_registry(clone)) == (True, 2, True, False, before)


@pytest.mark.process("git clone and git worktree add on scratch repositories, origin holding another run's branch")
def test_take_over_over_a_stale_fetched_branch_origin_holds_cuts_the_worktree_on_a_local_branch_at_origins_current_tip_4080(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "take-over")
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    scratch_git(upstream, "branch", "-q", "tdd/66-adopted", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    later = scratch_git(upstream, "commit-tree", "main^{tree}", "-p", "main", "-m", "the other machine's last push")
    scratch_git(upstream, "update-ref", "refs/heads/tdd/66-adopted", later)
    tip = scratch_git(upstream, "rev-parse", "refs/heads/tdd/66-adopted")
    want = scratch_wt_path(clone, 66)

    code, out, _ = run_cli(issue_worktree, ["--take-over", "66", "adopted"], cwd=clone)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"), scratch_git(want, "rev-parse", "HEAD")) == (
        0, want, "tdd/66-adopted", tip)


@pytest.mark.process("git worktree add on a scratch repository whose run directory holds a restored timeout pin")
def test_a_run_directory_holding_only_a_restored_timeout_pin_still_gets_its_worktree_with_the_pin_kept_4079(
        tmp_path, issue_worktree, run_cli):
    repo = scratch_repo(tmp_path / "restored-timeout")
    want = scratch_wt_path(repo, 67)
    pin = pathlib.Path(want, ".tdd", "issue-67-timeout")
    pin.parent.mkdir(parents=True)
    pin.write_text("3600\n")

    code, out, _ = run_cli(issue_worktree, ["67", "restored"], cwd=repo)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"), pin.read_text() if pin.exists() else None) == (
        0, want, "tdd/67-restored", "3600\n")


def resumed_on(worktree, code, out, local_tip, remote_tip):
    return (local_tip != remote_tip, code, out.strip(), scratch_git(worktree, "branch", "--show-current"),
            scratch_git(worktree, "rev-parse", "HEAD"))


@pytest.mark.process("git clone and git worktree add on scratch repositories, a local branch beside a fetched origin one")
def test_clone_holding_the_local_branch_while_origin_holds_it_too_and_the_remote_tracking_ref_is_fetched_still_starts_as_a_resume_on_the_local_tip_issue_1734(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "taken-over-resume")
    scratch_git(upstream, "branch", "-q", "tdd/65-took-over", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    scratch_git(clone, "branch", "-q", "tdd/65-took-over", "origin/tdd/65-took-over")
    scratch_git(clone, "switch", "-q", "-c", "scratch-65", "tdd/65-took-over")
    scratch_git(clone, "commit", "-q", "--allow-empty", "-m", "local work")
    scratch_git(clone, "branch", "-q", "-f", "tdd/65-took-over", "scratch-65")
    scratch_git(clone, "switch", "-q", "main")
    scratch_git(clone, "branch", "-q", "-D", "scratch-65")
    local_tip = scratch_git(clone, "rev-parse", "tdd/65-took-over")
    remote_tip = scratch_git(clone, "rev-parse", "refs/remotes/origin/tdd/65-took-over")
    mine = scratch_wt_path(clone, 65)

    code, out, _ = run_cli(issue_worktree, ["65", "took-over"], cwd=clone)

    assert resumed_on(mine, code, out, local_tip, remote_tip) == (True, 0, mine, "tdd/65-took-over", local_tip)


@pytest.mark.process("git clone and git worktree add on scratch repositories, the issue's worktree registered beside a fetched origin branch")
def test_clone_with_the_issues_worktree_registered_while_origin_holds_the_branch_and_the_remote_tracking_ref_is_fetched_still_starts_as_a_resume_on_the_branchs_own_tip_issue_1734(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "registered-resume")
    scratch_git(upstream, "branch", "-q", "tdd/66-registered", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    mine = scratch_wt_path(clone, 66)
    scratch_git(clone, "worktree", "add", "-q", "-b", "tdd/66-registered", mine, "origin/tdd/66-registered")
    scratch_git(mine, "commit", "-q", "--allow-empty", "-m", "local work")
    local_tip = scratch_git(mine, "rev-parse", "HEAD")
    remote_tip = scratch_git(clone, "rev-parse", "refs/remotes/origin/tdd/66-registered")

    code, out, _ = run_cli(issue_worktree, ["66", "registered"], cwd=clone)

    assert resumed_on(mine, code, out, local_tip, remote_tip) == (True, 0, mine, "tdd/66-registered", local_tip)


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_fresh_launch_onto_an_issue_whose_origin_branch_another_lane_claimed_exits_2_already_on_origin_and_creates_no_worktree_issue_3096(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], capture_output=True)
    seed = scratch_repo(tmp_path / "seed")
    scratch_git(seed, "switch", "-q", "-c", "tdd/9-slug")
    scratch_git(seed, "commit", "-q", "--allow-empty", "-m", "ledger")
    scratch_git(seed, "push", "-q", str(origin), "main", "tdd/9-slug")
    clone = tmp_path / "lane"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], capture_output=True)
    monkeypatch.setattr(sys.modules["github"], "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    want = scratch_wt_path(clone, 9)

    code, out, err = run_cli(issue_worktree, ["9", "slug"], cwd=clone)

    assert (code, out, "tdd/9-slug is already on origin — another run" in err,
            os.path.exists(want)) == (2, "", True, False)


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_resume_by_the_lane_that_took_the_issue_recreates_the_worktree_at_the_origin_branch_tip_with_its_committed_ledger_issue_3096(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], capture_output=True)
    seed = scratch_repo(tmp_path / "seed")
    scratch_git(seed, "switch", "-q", "-c", "tdd/9-slug")
    (seed / ".tdd").mkdir()
    (seed / ".tdd" / "issue-9.md").write_text("- [x] done step\n")
    scratch_git(seed, "add", ".tdd/issue-9.md")
    scratch_git(seed, "commit", "-q", "-m", "ledger")
    scratch_git(seed, "push", "-q", str(origin), "main", "tdd/9-slug")
    tip = scratch_git(seed, "rev-parse", "HEAD")
    clone = tmp_path / "lane"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], capture_output=True)
    monkeypatch.setattr(sys.modules["github"], "gh_issue_view", lambda number, field: "taken:main\n", raising=False)
    want = scratch_wt_path(clone, 9)

    code, out, _ = run_cli(issue_worktree, ["9", "slug"], cwd=clone)

    ledger = pathlib.Path(want, ".tdd", "issue-9.md")
    assert (code, out.strip(), ledger.read_text() if ledger.exists() else None,
            scratch_git(want, "rev-parse", "HEAD") if os.path.isdir(want) else None) == (
        0, want, "- [x] done step\n", tip)


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_resume_with_a_veri_label_carrying_a_lane_matches_the_taken_label_of_the_text_after_its_last_colon_issue_3096(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], capture_output=True)
    seed = scratch_repo(tmp_path / "seed")
    scratch_git(seed, "switch", "-q", "-c", "tdd/9-slug")
    scratch_git(seed, "commit", "-q", "--allow-empty", "-m", "ledger")
    scratch_git(seed, "push", "-q", str(origin), "main", "tdd/9-slug")
    clone = tmp_path / "lane"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], capture_output=True)
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:other")
    monkeypatch.setattr(sys.modules["github"], "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    want = scratch_wt_path(clone, 9)

    code, out, _ = run_cli(issue_worktree, ["9", "slug"], cwd=clone)

    assert (code, out.strip(), os.path.isdir(want)) == (0, want, True)


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_resume_by_lane_ma_is_refused_when_the_issue_carries_taken_main_since_the_lane_label_matches_whole_issue_3096(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], capture_output=True)
    seed = scratch_repo(tmp_path / "seed")
    scratch_git(seed, "switch", "-q", "-c", "tdd/9-slug")
    scratch_git(seed, "commit", "-q", "--allow-empty", "-m", "ledger")
    scratch_git(seed, "push", "-q", str(origin), "main", "tdd/9-slug")
    clone = tmp_path / "lane"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], capture_output=True)
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:ma")
    monkeypatch.setattr(sys.modules["github"], "gh_issue_view", lambda number, field: "taken:main\n", raising=False)
    want = scratch_wt_path(clone, 9)

    code, out, _ = run_cli(issue_worktree, ["9", "slug"], cwd=clone)

    assert (code, out, os.path.exists(want)) == (2, "", False)


@pytest.mark.process("git clone of a local bare origin and git worktree add on a scratch repository, the lane lookup faked")
def test_a_resume_under_another_slug_reuses_the_issues_one_local_branch_and_cuts_no_new_one_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "reuse-upstream")
    bare = tmp_path / "reuse-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "reuse-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    scratch_git(clone, "branch", "tdd/3765-alpha-beta")
    scratch_git(clone, "push", "-q", "origin", "tdd/3765-alpha-beta")
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:main")
    want = scratch_wt_path(clone, 3765)

    code, out, _ = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"),
            scratch_git(clone, "branch", "--list", "tdd/3765-gamma-delta")) == (0, want, "tdd/3765-alpha-beta", "")


@pytest.mark.process("git clone of a local bare origin and git worktree add on a scratch repository, the lane lookup faked")
def test_a_resume_under_another_slug_reuses_the_issues_one_packed_branch_and_ignores_a_longer_issue_number_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "packed-upstream")
    bare = tmp_path / "packed-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "packed-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    for branch in ("tdd/3765-alpha-beta", "tdd/37650-other"):
        scratch_git(clone, "branch", branch)
        scratch_git(clone, "push", "-q", "origin", branch)
    scratch_git(clone, "pack-refs", "--all")
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:main")
    want = scratch_wt_path(clone, 3765)

    code, out, _ = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current"),
            scratch_git(clone, "branch", "--list", "tdd/3765-gamma-delta")) == (0, want, "tdd/3765-alpha-beta", "")


@pytest.mark.process("git clone of a local bare origin and git worktree add on a scratch repository, the lane lookup faked")
def test_a_resume_under_another_slug_reuses_the_issues_one_origin_only_branch_taken_by_this_lane_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "origin-only-upstream")
    bare = tmp_path / "origin-only-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "origin-only-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    scratch_git(clone, "branch", "tdd/3765-alpha-beta")
    scratch_git(clone, "push", "-q", "origin", "tdd/3765-alpha-beta")
    scratch_git(clone, "branch", "-q", "-D", "tdd/3765-alpha-beta")
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:main")
    want = scratch_wt_path(clone, 3765)

    code, out, _ = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out.strip(), scratch_git(want, "branch", "--show-current") if os.path.isdir(want) else None,
            scratch_git(clone, "branch", "--list", "tdd/3765-gamma-delta")) == (0, want, "tdd/3765-alpha-beta", "")


@pytest.mark.process("git clone of a local bare origin and git worktree add on a scratch repository, the lane lookup faked")
def test_a_resume_under_another_slug_still_refuses_an_origin_only_branch_another_lane_took_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "other-lane-upstream")
    bare = tmp_path / "other-lane-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "other-lane-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    scratch_git(clone, "branch", "tdd/3765-alpha-beta")
    scratch_git(clone, "push", "-q", "origin", "tdd/3765-alpha-beta")
    scratch_git(clone, "branch", "-q", "-D", "tdd/3765-alpha-beta")
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:other")
    want = scratch_wt_path(clone, 3765)

    code, out, _ = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out, os.path.exists(want),
            scratch_git(clone, "branch", "--list", "tdd/3765-gamma-delta")) == (2, "", False, "")


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_a_resume_under_another_slug_with_two_of_the_issues_branches_exits_2_naming_both_and_the_requested_one_creating_no_worktree_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "two-upstream")
    bare = tmp_path / "two-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "two-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    for branch in ("tdd/3765-alpha-beta", "tdd/3765-epsilon"):
        scratch_git(clone, "branch", branch)
        scratch_git(clone, "push", "-q", "origin", branch)
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:main")
    want = scratch_wt_path(clone, 3765)

    code, out, err = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out, os.path.exists(want),
            [name in err for name in ("tdd/3765-alpha-beta", "tdd/3765-epsilon", "tdd/3765-gamma-delta")]) == (
        2, "", False, [True, True, True])


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_a_resume_under_another_slug_with_two_origin_only_branches_exits_2_naming_both_and_the_requested_one_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "two-remote-upstream")
    bare = tmp_path / "two-remote-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "two-remote-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    for branch in ("tdd/3765-alpha-beta", "tdd/3765-epsilon"):
        scratch_git(clone, "branch", branch)
        scratch_git(clone, "push", "-q", "origin", branch)
        scratch_git(clone, "branch", "-q", "-D", branch)
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:main")
    want = scratch_wt_path(clone, 3765)

    code, out, err = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out, os.path.exists(want),
            [name in err for name in ("tdd/3765-alpha-beta", "tdd/3765-epsilon", "tdd/3765-gamma-delta")]) == (
        2, "", False, [True, True, True])


@pytest.mark.process("git clone, push and worktree add against a local bare repository as origin")
def test_a_resume_under_another_slug_with_one_local_and_a_different_origin_only_branch_exits_2_naming_both_issue_3765(
        tmp_path, monkeypatch, issue_worktree, run_cli):
    upstream = scratch_repo(tmp_path / "mixed-upstream")
    bare = tmp_path / "mixed-origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(upstream), str(bare)], capture_output=True)
    clone = tmp_path / "mixed-clone"
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], capture_output=True)
    scratch_git(clone, "branch", "tdd/3765-alpha-beta")
    scratch_git(clone, "branch", "tdd/3765-epsilon")
    scratch_git(clone, "push", "-q", "origin", "tdd/3765-epsilon")
    scratch_git(clone, "branch", "-q", "-D", "tdd/3765-epsilon")
    monkeypatch.setattr(issue_worktree.github, "gh_issue_view", lambda issue, field: "taken:main")
    want = scratch_wt_path(clone, 3765)

    code, out, err = run_cli(issue_worktree, ["3765", "gamma-delta"], cwd=clone)

    assert (code, out, os.path.exists(want),
            [name in err for name in ("tdd/3765-alpha-beta", "tdd/3765-epsilon", "tdd/3765-gamma-delta")]) == (
        2, "", False, [True, True, True])

"""In-process cases for veri/issue_worktree.py, the module issue-worktree.sh is a shim over."""
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

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>\n"


@pytest.fixture(autouse=True)
def case_works_in_its_scratch_tree(tmp_path, monkeypatch):
    """issue_worktree.py runs git with no cwd; from the case's own tmp_path the git guard sees every call."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def issue_worktree():
    return importlib.import_module("veri.issue_worktree")


def fake_git(monkeypatch, answers):
    """subprocess.run answering each git argv tuple in <answers> with (exit code, stdout); every call recorded."""
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        code, stdout = answers.get(tuple(args), (None, None))
        if code is None:
            raise AssertionError("unexpected command: %r" % (args,))
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, stdout, "")
        return subprocess.CompletedProcess(args, code, stdout, "")

    def refused(*args, **kwargs):
        calls.append(list(args[0]) if args else kwargs)
        raise AssertionError("unexpected process: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    for name in ("Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
        monkeypatch.setattr(subprocess, name, refused)
    return calls


def test_main_refuses_a_bad_argument_list_with_the_usage_line_before_any_git_and_maps_a_dying_git_to_2(
        monkeypatch, capsys, issue_worktree):
    for argv in ([], ["270"], ["--remove"], ["", "x"], ["7", ""]):
        calls = fake_git(monkeypatch, {})

        code = issue_worktree.main(argv)

        assert (argv, code, calls, capsys.readouterr()[:]) == (argv, 2, [], ("", USAGE))

    calls = fake_git(monkeypatch, {("git", "worktree", "list", "--porcelain"): (128, "")})

    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr().out, calls[:1]) == (2, "", [["git", "worktree", "list", "--porcelain"]])


def test_cli_hands_back_a_registered_worktree_whose_pid_file_holds_non_utf8_bytes_with_nothing_on_stderr_issue_965(
        monkeypatch, tmp_path, issue_worktree, run_cli):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/965"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree %s\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/965-non-utf8\n\n"
                % (main_tree, path))
    listing = ("git", "worktree", "list", "--porcelain")
    pid_file = pathlib.Path(path) / ".tdd" / "conductor.pid"
    pid_file.parent.mkdir(parents=True)
    pid_file.write_bytes(b"\xff\xfe\n")
    routing_git(monkeypatch, {listing: (0, registry, "")})

    code, out, err = run_cli(issue_worktree, ["965", "non-utf8"], cwd=tmp_path)

    assert (code, out, err) == (0, path + "\n", "")


def test_cli_hand_back_leaves_a_marker_in_the_worktrees_tdd_dir_with_the_path_alone_on_stdout_issue_2460(
        monkeypatch, tmp_path, issue_worktree, run_cli):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/2460"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree %s\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/2460-marker\n\n"
                % (main_tree, path))
    listing = ("git", "worktree", "list", "--porcelain")
    tdd = pathlib.Path(path) / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "events.jsonl").write_text("")
    routing_git(monkeypatch, {listing: (0, registry, "")})

    code, out, err = run_cli(issue_worktree, ["2460", "marker"], cwd=tmp_path)

    marker = sorted(p.name for p in tdd.iterdir() if p.name != "events.jsonl")
    assert (code, out, err, len(marker)) == (0, path + "\n", "", 1)


def test_cli_refuses_an_n_that_is_not_a_positive_whole_number_with_the_usage_line_and_runs_no_git(
        monkeypatch, tmp_path, issue_worktree, run_cli):
    for n in ("abc", "0", "-3", "7a", "../escape"):
        calls = fake_git(monkeypatch, {})

        code, out, err = run_cli(issue_worktree, [n, "slug"], cwd=tmp_path)

        assert (n, code, out, err, calls, sorted(tmp_path.rglob("*"))) == (n, 2, "", USAGE, [], [])


def test_cli_remove_refuses_an_n_that_is_not_a_positive_whole_number_with_the_usage_line_and_runs_no_git(
        monkeypatch, tmp_path, issue_worktree, run_cli):
    victim = tmp_path / ".claude" / "worktrees" / "victim"
    victim.mkdir(parents=True)
    for n in ("abc", "0", "-3", "../../.claude/worktrees/victim"):
        calls = fake_git(monkeypatch, {})

        code, out, err = run_cli(issue_worktree, ["--remove", n], cwd=tmp_path)

        assert (n, code, out, err, calls, victim.is_dir()) == (n, 2, "", USAGE, [], True)


def routing_git(monkeypatch, answers):
    """subprocess.run answering each git argv tuple in <answers> with (exit code, stdout, stderr), each stream sent where the call routes it."""
    calls = []

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

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        code, stdout, stderr = answers[tuple(args)]
        captured = kwargs.get("capture_output")
        out_to = subprocess.PIPE if captured else kwargs.get("stdout")
        err_to = subprocess.PIPE if captured else kwargs.get("stderr")
        deliver(stdout, out_to)
        deliver(stderr, 2 if err_to is None else err_to)
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, stdout, stderr)
        return subprocess.CompletedProcess(
            args, code, stdout if out_to == subprocess.PIPE else None, stderr if err_to == subprocess.PIPE else None)

    def refused(*args, **kwargs):
        raise AssertionError("unexpected process: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    for name in ("Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
        monkeypatch.setattr(subprocess, name, refused)
    return calls


def test_main_remove_refuses_a_dirty_worktree_and_removes_a_clean_one_without_force_at_the_unnormalised_registry_path(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/a/../repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree /srv/other\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/x\n\n" % main_tree)
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)

    calls = routing_git(monkeypatch, {listing: (0, registry, ""), status: (0, "?? stray\n", "")})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == list(remove[:3])]) == (
        2, ("", "issue-worktree: %s has uncommitted changes — refusing to remove it\n" % path), [])

    for argv in (["--remove", "7"], ["--remove", "7", "extra"]):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), status: (0, "", ""),
                                          remove: (0, "removed it\n", "")})
        code = issue_worktree.main(argv)
        assert (argv, code, capsys.readouterr()[:], calls) == (
            argv, 0, ("", "removed it\n"), [list(listing), list(status), list(remove)])

    calls = routing_git(monkeypatch, {listing: (0, registry, ""),
                                      status: (128, "", "fatal: cannot change to '%s'\n" % path),
                                      remove: (128, "", "fatal: '%s' is not a working tree\n" % path)})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr().out, calls) == (2, "", [list(listing), list(status), list(remove)])


def test_main_remove_returns_a_dying_gits_status_inside_0_to_3_as_it_is_and_maps_only_one_outside_to_2(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)

    calls = routing_git(monkeypatch, {listing: (1, "", "error: listing failed\n")})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr().out, calls) == (1, "", [list(listing)])

    for remove_code, want in ((1, 1), (128, 2)):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), status: (0, "", ""),
                                          remove: (remove_code, "", "error: remove failed\n")})
        code = issue_worktree.main(["--remove", "7"])
        assert (remove_code, code, capsys.readouterr().out, calls) == (
            remove_code, want, "", [list(listing), list(status), list(remove)])


@pytest.mark.process("a stand-in conductor (a claude under run_conductor.py) left running beside real git worktree calls")
def test_main_hands_back_a_registered_worktree_by_n_alone_unless_its_pid_file_names_a_live_conductor(
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
        calls = routing_git(monkeypatch, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", slug])
        assert (slug, code, capfd.readouterr()[:], calls) == (slug, 0, (path + "\n", ""), [list(listing)])

    pid_file = pathlib.Path(path) / ".tdd" / "conductor.pid"
    pid_file.parent.mkdir(parents=True)
    for content in ("4242\r\n", "pid 4242\n", "-4242\n", "1\n", "999\n", "99999999999999999999\n", "", "\n", "0\n"):
        pid_file.write_text(content)
        calls = routing_git(monkeypatch, {listing: (0, registry, "")})
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


def test_main_hands_back_a_registered_worktree_whose_pid_file_holds_0_or_00_issue_819(
        capsys, tmp_path, issue_worktree, monkeypatch):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/7"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree %s\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/7-slug\n\n"
                % (main_tree, path))
    listing = ("git", "worktree", "list", "--porcelain")
    pid_file = pathlib.Path(path) / ".tdd" / "conductor.pid"
    pid_file.parent.mkdir(parents=True)
    for content in ("0\n", "00\n"):
        pid_file.write_text(content)
        calls = routing_git(monkeypatch, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", "slug"])
        assert (content, code, capsys.readouterr()[:], calls) == (content, 0, (path + "\n", ""), [list(listing)])


def test_main_hands_back_a_registered_worktree_whose_pid_file_open_cannot_read_issue_965(
        capsys, tmp_path, issue_worktree, monkeypatch):
    import builtins

    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/7"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree %s\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/7-slug\n\n"
                % (main_tree, path))
    listing = ("git", "worktree", "list", "--porcelain")
    pid_file = pathlib.Path(path) / ".tdd" / "conductor.pid"
    pid_file.parent.mkdir(parents=True)
    pid_file.write_text("4242\n")
    real_open = builtins.open

    def fake_open(file, *args, **kwargs):
        if os.fspath(file) == str(pid_file):
            raise PermissionError(13, "Permission denied", str(pid_file))
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)
    calls = routing_git(monkeypatch, {listing: (0, registry, "")})
    code = issue_worktree.main(["7", "slug"])
    assert (code, capsys.readouterr()[:], calls) == (0, (path + "\n", ""), [list(listing)])


def test_main_refuses_a_branch_any_registry_entry_has_checked_out_the_main_working_tree_included_before_any_cut(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    elsewhere = "/srv/elsewhere"
    listing = ("git", "worktree", "list", "--porcelain")
    owned = "issue-worktree: branch tdd/5-x is already checked out in %s — another conductor owns it\n"
    registries = (
        ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/tdd/5-x\n\n" % main_tree,
         main_tree),
        ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
         "worktree %s\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/5-x\n\n"
         % (main_tree, elsewhere), elsewhere),
    )

    for registry, holder in registries:
        calls = routing_git(monkeypatch, {listing: (0, registry, "")})
        code = issue_worktree.main(["5", "x"])
        assert (holder, code, capsys.readouterr()[:], calls) == (holder, 2, ("", owned % holder), [list(listing)])


def test_main_checks_out_a_local_branch_and_maps_a_dying_add_to_2(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    checkout = ("git", "worktree", "add", "-q", path, "tdd/7-slug")

    for add_code, want, out in ((0, 0, path + "\n"), (128, 2, "")):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), local: (0, "", ""),
                                          checkout: (add_code, "Preparing worktree\n", "")})
        code = issue_worktree.main(["7", "slug"])
        assert (add_code, code, capsys.readouterr()[:], calls) == (
            add_code, want, (out, "Preparing worktree\n"), [list(listing), list(local), list(checkout)])


def test_main_refuses_a_fresh_run_whose_fetched_branch_origin_still_holds_and_adds_no_worktree_issue_1734(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")

    calls = routing_git(monkeypatch, {
        listing: (0, registry, ""), local: (1, "", ""), remote: (0, "", ""),
        claims: (0, "1111111111111111111111111111111111111111\trefs/heads/tdd/7-slug\n", "")})
    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == ["git", "worktree", "add"]]) == (
        2, ("", "issue-worktree: tdd/7-slug is already on origin — another run holds it;"
                " to take it over run: git branch tdd/7-slug origin/tdd/7-slug\n"), [])


def test_main_cuts_a_fresh_branch_from_the_default_when_only_a_stale_remote_tracking_ref_names_the_issue_issue_1734(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    get_url = ("git", "remote", "get-url", "origin")
    fetch = ("git", "fetch", "-q", "origin", "trunk")
    fresh = ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", path, "origin/trunk")
    stale = ("git", "worktree", "add", "-q", "-b", "tdd/7-slug", path, "refs/remotes/origin/tdd/7-slug")

    calls = routing_git(monkeypatch, {
        listing: (0, registry, ""), local: (1, "", ""), remote: (0, "", ""), claims: (0, "", ""),
        symref: (0, "origin/trunk\n", ""), get_url: (0, "/srv/origin.git\n", ""),
        fetch: (0, "", ""), fresh: (0, "", ""), stale: (0, "", "")})
    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == ["git", "worktree", "add"]]) == (
        0, (path + "\n", ""), [list(fresh)])


def test_main_names_the_default_branch_from_origin_head_else_from_the_remotes_symref_and_refuses_when_neither_names_one(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    get_url = ("git", "remote", "get-url", "origin")
    ls_remote = ("git", "ls-remote", "--symref", "origin", "HEAD")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")
    refusal = ("issue-worktree: cannot determine origin's default branch"
               " (no refs/remotes/origin/HEAD, and the remote did not name one)\n")
    sha = "2222222222222222222222222222222222222222"

    def run(answers):
        recorded = routing_git(monkeypatch, answers)
        code = issue_worktree.main(["7", "slug"])
        calls = [tuple(c) for c in recorded]
        return code, capsys.readouterr()[:], calls

    base = {listing: (0, registry, ""), local: (1, "", ""), remote: (1, "", ""),
            get_url: (0, "/srv/origin.git\n", "url noise\n"),
            claims: (0, "", "")}
    named = (
        ("origin/HEAD", {symref: (0, "origin/trunk\n", "")}, "trunk"),
        ("symref", {symref: (1, "", "symref noise\n"),
                    ls_remote: (0, "ref: refs/heads/develop\tHEAD\n%s\tHEAD\n" % sha, "ls noise\n")}, "develop"),
        ("symref, exit ignored", {symref: (1, "", ""),
                                  ls_remote: (2, "ref: refs/heads/develop\tHEAD\n", "")}, "develop"),
        ("symref, no prefix stripped", {symref: (1, "", ""),
                                        ls_remote: (0, "ref: refs/heads/origin/x\tHEAD\n", "")}, "origin/x"),
    )
    for label, answers, name in named:
        fetch = ("git", "fetch", "-q", "origin", name)
        add = ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", f"{main_tree}/.tdd/wt/7", "origin/" + name)
        code, (out, err), calls = run({**base, **answers, fetch: (0, "", ""), add: (0, "", "")})
        before = calls[:calls.index(fetch)] if fetch in calls else calls
        assert (label, fetch in calls, calls.count(get_url),
                [c for c in calls if c[-1] in ("refs/heads/main", "refs/heads/master")],
                "noise" in out + err) == (label, True, 1, [], False)
        assert (label, sorted(set(before) - {ls_remote})) == (label, sorted({listing, local, remote, symref, get_url, claims}))

    unnamed = (
        ("no ref: line", (0, "%s\tHEAD\n" % sha, "ls noise\n")),
        ("unreachable", (128, "", "fatal: could not read from remote repository\n")),
        ("outside refs/heads", (0, "ref: refs/tags/v1\tHEAD\n%s\tHEAD\n" % sha, "")),
    )
    for label, answer in unnamed:
        code, captured, calls = run({**base, symref: (1, "", "symref noise\n"), ls_remote: answer})
        assert (label, code, captured, calls[-1], sorted(calls)) == (
            label, 2, ("", refusal), ls_remote, sorted([listing, local, remote, symref, get_url, claims, ls_remote]))


def test_main_falls_back_to_a_local_main_then_master_only_without_an_origin_remote_and_refuses_when_neither_exists(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    get_url = ("git", "remote", "get-url", "origin")
    ls_remote = ("git", "ls-remote", "--symref", "origin", "HEAD")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")
    main = ("git", "show-ref", "--verify", "--quiet", "refs/heads/main")
    master = ("git", "show-ref", "--verify", "--quiet", "refs/heads/master")
    refusal = "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)\n"

    def cut(name):
        return ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", path, name)

    base = {listing: (0, registry, ""), local: (1, "", ""), remote: (1, "", ""),
            symref: (1, "", "symref noise\n"), get_url: (2, "", "error: No such remote 'origin'\n"),
            ls_remote: (128, "", "fatal: 'origin' does not appear to be a git repository\n"),
            cut("main"): (0, "", ""), cut("master"): (0, "", "")}
    for label, main_code, master_code, want in (
            ("main", 0, 0, (0, (path + "\n", ""), cut("main"))),
            ("master", 1, 0, (0, (path + "\n", ""), cut("master"))),
            ("neither", 1, 1, (2, ("", refusal), None))):
        recorded = routing_git(monkeypatch, {**base, main: (main_code, "", ""), master: (master_code, "", "")})
        code = issue_worktree.main(["7", "slug"])
        calls = [tuple(c) for c in recorded]
        adds = [c for c in calls if c[1:3] == ("worktree", "add")]
        assert (label, code, capsys.readouterr()[:], adds[-1] if adds else None,
                [c for c in calls if c[1] in ("fetch", "ls-remote")]) == (label, *want, [])


def test_main_cuts_from_a_fetched_origin_default_with_no_track_and_refuses_to_cut_from_a_stale_one_when_the_fetch_fails(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    get_url = ("git", "remote", "get-url", "origin")
    fetch = ("git", "fetch", "-q", "origin", "trunk")
    add = ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", path, "origin/trunk")
    refusal = ("issue-worktree: git fetch origin trunk failed"
               " — refusing to cut tdd/7-slug from a stale origin/trunk\n")
    base = {listing: (0, registry, ""), local: (1, "", ""), remote: (1, "", ""),
            symref: (0, "origin/trunk\n", ""), get_url: (0, "/srv/origin.git\n", ""),
            ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*"): (0, "", ""),
            add: (0, "", "")}

    recorded = routing_git(monkeypatch, {**base, fetch: (0, "fetched\n", "")})
    code = issue_worktree.main(["7", "slug"])
    assert (code, capsys.readouterr()[:], [tuple(c) for c in recorded][-2:]) == (0, (path + "\n", "fetched\n"), [fetch, add])

    recorded = routing_git(monkeypatch, {**base, fetch: (1, "", "fatal: couldn't find remote ref trunk\n")})
    code = issue_worktree.main(["7", "slug"])
    out, err = capsys.readouterr()
    assert (code, out, err[-len(refusal):], [tuple(c) for c in recorded if c[1:3] == ["worktree", "add"]]) == (
        2, "", refusal, [])


def test_main_puts_a_seeded_log_back_when_the_cut_dies_and_still_maps_the_dying_add_into_0_to_3(
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
    routing_git(monkeypatch, {
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
def test_main_leaves_a_path_holding_more_than_the_seeded_log_where_it_is_for_git_to_refuse(
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
    routing_git(monkeypatch, {
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


def test_main_appends_a_seeded_log_into_the_tdd_directory_a_successful_cut_checked_out(
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
    routing_git(monkeypatch, {
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


def test_main_restores_a_seeded_log_after_a_successful_cut_without_issue_worktree_opening_events_jsonl_itself(
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
    routing_git(monkeypatch, {
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


def test_main_puts_a_seeded_log_back_when_it_refuses_for_the_origin_default_the_missing_default_or_the_failed_fetch(
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
        routing_git(monkeypatch, {**base, **answers})
        routed = subprocess.run
        path_at_refusal = []

        def run(args, **kwargs):
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


def test_main_answers_each_ls_remote_shape_with_its_stdout_stderr_and_exit_code_when_origin_head_is_unset(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    sha = "2222222222222222222222222222222222222222"
    base = {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug"): (1, "", ""),
        ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"): (
            1, "", "fatal: ref refs/remotes/origin/HEAD is not a symbolic ref\n"),
        ("git", "remote", "get-url", "origin"): (0, "/srv/origin.git\n", ""),
        ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*"): (0, "", ""),
        ("git", "fetch", "-q", "origin", "trunk"): (0, "", ""),
        ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", path, "origin/trunk"): (0, "", ""),
    }
    ls_remote = ("git", "ls-remote", "--symref", "origin", "HEAD")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")

    def run(answer):
        routing_git(monkeypatch, {**base, ls_remote: answer})
        code = issue_worktree.main(["7", "slug"])
        out, err = capsys.readouterr()
        return code, out, err

    symref = run((0, "ref: refs/heads/trunk\tHEAD\n%s\tHEAD\n" % sha, ""))
    no_symref = run((0, "%s\tHEAD\n" % sha, ""))
    unreachable = run((128, "", "fatal: unable to access 'https://example.invalid/repo.git/': Could not resolve host\n"))

    refusal = ("issue-worktree: cannot determine origin's default branch"
               " (no refs/remotes/origin/HEAD, and the remote did not name one)\n")
    assert symref == (0, path + "\n", "")
    assert no_symref == (2, "", refusal)
    assert unreachable == (2, "", refusal)


def _open_prs(issue_worktree, monkeypatch, prs):
    """claiming_pr on a github.com origin, with gh_json answering `prs`; returns (its answer, the fixtures asked)."""
    asked = []

    def fake_gh_json(*args):
        asked.append(args[0])
        return json.dumps(prs)

    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    monkeypatch.setattr(issue_worktree, "gh_json", fake_gh_json)
    return issue_worktree.claiming_pr("62", "https://github.com/o/r.git"), asked


def test_claiming_pr_1656_asks_github_for_a_github_com_origin_and_names_the_open_pr_that_closes_the_issue_not_one_listed_before_it(issue_worktree, monkeypatch):
    prs = [{"state": "OPEN", "body": "Closes #63", "url": "https://github.com/o/r/pull/10"},
           {"state": "OPEN", "body": "Fixes it.\n\nCloses #62", "url": "https://github.com/o/r/pull/9"}]

    assert _open_prs(issue_worktree, monkeypatch, prs) == ("https://github.com/o/r/pull/9", ["prs.json"])


def test_claiming_pr_1656_names_no_pr_on_a_github_com_origin_when_the_only_open_one_closes_another_issue(issue_worktree, monkeypatch):
    prs = [{"state": "OPEN", "body": "Closes #63", "url": "https://github.com/o/r/pull/10"}]

    assert _open_prs(issue_worktree, monkeypatch, prs) == ("", ["prs.json"])


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
    seen = lambda: (scratch_git(clone, "rev-parse", "refs/heads/main"), scratch_git(clone, "rev-parse", "HEAD"),
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


def test_the_escape_guard_fails_a_case_whose_subject_runs_git_from_the_repository_the_tests_live_in_not_its_scratch_repository(
        monkeypatch, issue_worktree):
    monkeypatch.chdir(pathlib.Path(__file__).resolve().parents[5])

    with pytest.raises(AssertionError, match="starts git against the repository the tests live in"):
        issue_worktree.main(["7", "slug"])


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
    gh = prs_fixture(tmp_path, [{"body": "Closes #62", "state": "OPEN", "isDraft": True,
                                 "url": "https://example.test/pull/620"}])
    before = (scratch_registry(clone), commits(clone))

    code, _, err = run_cli(issue_worktree, ["62", "fresh-start"], cwd=clone, env={"VERI_GH_JSON": gh})

    assert (code, "pull/620" in err, os.path.exists(want), (scratch_registry(clone), commits(clone))) == (
        2, True, False, before)


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
    gh = prs_fixture(tmp_path, [{"body": "Closes #63", "state": "OPEN", "isDraft": True,
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
    page = json.dumps([{"body": "Closes #66", "state": "OPEN", "url": "https://ghe.example.test/acme/veri/pull/660"}])

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
def test_fresh_call_over_a_fetched_remote_tracking_ref_of_a_branch_origin_holds_exits_2_naming_the_branch_and_the_git_branch_command_that_takes_the_run_over_creating_no_worktree_or_branch_issue_1734(
        tmp_path, issue_worktree, run_cli):
    upstream, clone = scratch_clone(tmp_path, "fetched-claimed")
    scratch_git(upstream, "branch", "-q", "tdd/64-taken-over", "main")
    scratch_git(clone, "fetch", "-q", "origin")
    want = scratch_wt_path(clone, 64)
    fetched = scratch_git(clone, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/tdd/64-taken-over")
    before = scratch_registry(clone)

    code, _, err = run_cli(issue_worktree, ["64", "taken-over"], cwd=clone)

    assert (bool(fetched), code, "git branch tdd/64-taken-over origin/tdd/64-taken-over" in err,
            os.path.exists(want), scratch_registry(clone)) == (True, 2, True, False, before)


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


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path, monkeypatch, issue_worktree):
    import importlib.util
    real = pathlib.Path(issue_worktree.__file__).resolve()
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(real, farm / "issue_worktree.py")
    spec = importlib.util.spec_from_file_location("symlinked_issue_worktree", farm / "issue_worktree.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    monkeypatch.chdir(real.parent.parent)

    assert loaded.inside_own_scripts() is True

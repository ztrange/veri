"""In-process cases for veri/issue_worktree.py, the module issue-worktree.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>\n"


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


def test_main_hands_back_a_registered_worktree_by_n_alone_unless_its_pid_file_names_a_live_conductor(
        monkeypatch, capsys, tmp_path, issue_worktree):
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
        assert (slug, code, capsys.readouterr()[:], calls) == (slug, 0, (path + "\n", ""), [list(listing)])

    pid_file = pathlib.Path(path) / ".tdd" / "conductor.pid"
    pid_file.parent.mkdir(parents=True)
    held = "issue-worktree: %s is held by a live conductor (pid %s) — refusing to hand back a run in flight\n"
    for content, digits in ((" \t4242\t \nignored\n", "4242"), ("004242\n", "004242")):
        pid_file.write_text(content)
        calls = routing_git(monkeypatch, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", "slug"])
        assert (content, code, capsys.readouterr()[:], calls) == (
            content, 2, ("", held % (path, digits)), [list(listing)])

    for content in ("4242\r\n", "pid 4242\n", "-4242\n", "1\n", "999\n", "99999999999999999999\n", "", "\n", "0\n"):
        pid_file.write_text(content)
        calls = routing_git(monkeypatch, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", "slug"])
        assert (content, code, capsys.readouterr()[:], calls) == (content, 0, (path + "\n", ""), [list(listing)])


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


def test_main_checks_out_a_local_branch_else_cuts_from_the_remote_one_without_a_fetch_and_maps_a_dying_add_to_2(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    checkout = ("git", "worktree", "add", "-q", path, "tdd/7-slug")
    track = ("git", "worktree", "add", "-q", "-b", "tdd/7-slug", path, "refs/remotes/origin/tdd/7-slug")

    for add_code, want, out in ((0, 0, path + "\n"), (128, 2, "")):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), local: (0, "", ""),
                                          checkout: (add_code, "Preparing worktree\n", "")})
        code = issue_worktree.main(["7", "slug"])
        assert (add_code, code, capsys.readouterr()[:], calls) == (
            add_code, want, (out, "Preparing worktree\n"), [list(listing), list(local), list(checkout)])

    for add_code, want, out in ((0, 0, path + "\n"), (128, 2, "")):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), local: (1, "", ""), remote: (0, "", ""),
                                          track: (add_code, "Preparing worktree\n", "")})
        code = issue_worktree.main(["7", "slug"])
        assert (add_code, code, capsys.readouterr()[:], calls) == (
            add_code, want, (out, "Preparing worktree\n"), [list(listing), list(local), list(remote), list(track)])


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
    refusal = ("issue-worktree: cannot determine origin's default branch"
               " (no refs/remotes/origin/HEAD, and the remote did not name one)\n")
    sha = "2222222222222222222222222222222222222222"

    def run(answers):
        recorded = routing_git(monkeypatch, answers)
        code = issue_worktree.main(["7", "slug"])
        calls = [tuple(c) for c in recorded]
        return code, capsys.readouterr()[:], calls

    base = {listing: (0, registry, ""), local: (1, "", ""), remote: (1, "", ""),
            get_url: (0, "https://example.invalid/repo.git\n", "url noise\n")}
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
        assert (label, sorted(set(before) - {ls_remote})) == (label, sorted({listing, local, remote, symref, get_url}))

    unnamed = (
        ("no ref: line", (0, "%s\tHEAD\n" % sha, "ls noise\n")),
        ("unreachable", (128, "", "fatal: could not read from remote repository\n")),
        ("outside refs/heads", (0, "ref: refs/tags/v1\tHEAD\n%s\tHEAD\n" % sha, "")),
    )
    for label, answer in unnamed:
        code, captured, calls = run({**base, symref: (1, "", "symref noise\n"), ls_remote: answer})
        assert (label, code, captured, calls[-1], sorted(calls)) == (
            label, 2, ("", refusal), ls_remote, sorted([listing, local, remote, symref, get_url, ls_remote]))


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
            symref: (0, "origin/trunk\n", ""), get_url: (0, "https://example.invalid/repo.git\n", ""),
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
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/63-own-trap"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/63-own-trap"): (1, "", ""),
    }
    refusals = (
        ("origin default", ls_remote,
         {symref: (1, "", ""), get_url: (0, "https://example.invalid/repo.git\n", ""), ls_remote: (128, "", "")},
         "issue-worktree: cannot determine origin's default branch"
         " (no refs/remotes/origin/HEAD, and the remote did not name one)\n"),
        ("no origin", ("git", "show-ref", "--verify", "--quiet", "refs/heads/master"),
         {symref: (1, "", ""), get_url: (2, "", ""),
          ("git", "show-ref", "--verify", "--quiet", "refs/heads/main"): (1, "", ""),
          ("git", "show-ref", "--verify", "--quiet", "refs/heads/master"): (1, "", "")},
         "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)\n"),
        ("fetch", fetch,
         {symref: (0, "origin/trunk\n", ""), get_url: (0, "https://example.invalid/repo.git\n", ""),
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

"""In-process cases for veri/issue_worktree.py, the module issue-worktree.sh is a shim over."""
import collections.abc
import importlib
import json
import os
import pathlib
import subprocess
import sys

import pytest

USAGE = "usage: issue-worktree.sh [--take-over] <n> <slug> | --remove <n>\n"


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


def fake_git(fake_processes, answers):
    """fake_processes answering each git argv tuple in <answers> with (exit code, stdout); every call recorded."""
    table = {" ".join(argv): (code, stdout, "") for argv, (code, stdout) in answers.items()}
    return Argvs(fake_processes.answers(table, exact=True))


def test_main_refuses_a_bad_argument_list_with_the_usage_line_before_any_git_and_maps_a_dying_git_to_2(fake_processes, 
        monkeypatch, capsys, issue_worktree):
    for argv in ([], ["270"], ["--remove"], ["", "x"], ["7", ""]):
        calls = fake_git(fake_processes, {})

        code = issue_worktree.main(argv)

        assert (argv, code, calls, capsys.readouterr()[:]) == (argv, 2, [], ("", USAGE))

    calls = fake_git(fake_processes, {("git", "worktree", "list", "--porcelain"): (128, "")})

    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr().out, calls[:1]) == (2, "", [["git", "worktree", "list", "--porcelain"]])


def test_cli_hands_back_a_registered_worktree_whose_pid_file_holds_non_utf8_bytes_with_nothing_on_stderr_issue_965(fake_processes, 
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
    routing_git(fake_processes, {listing: (0, registry, "")})

    code, out, err = run_cli(issue_worktree, ["965", "non-utf8"], cwd=tmp_path)

    assert (code, out, err) == (0, path + "\n", "")


def test_cli_hand_back_leaves_a_marker_in_the_worktrees_tdd_dir_with_the_path_alone_on_stdout_issue_2460(fake_processes, 
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
    routing_git(fake_processes, {listing: (0, registry, "")})

    code, out, err = run_cli(issue_worktree, ["2460", "marker"], cwd=tmp_path)

    marker = sorted(p.name for p in tdd.iterdir() if p.name != "events.jsonl")
    assert (code, out, err, len(marker)) == (0, path + "\n", "", 1)


def test_cli_refuses_an_n_that_is_not_a_positive_whole_number_with_the_usage_line_and_runs_no_git(fake_processes, 
        monkeypatch, tmp_path, issue_worktree, run_cli):
    for n in ("abc", "0", "-3", "7a", "../escape"):
        calls = fake_git(fake_processes, {})

        code, out, err = run_cli(issue_worktree, [n, "slug"], cwd=tmp_path)

        assert (n, code, out, err, calls, sorted(tmp_path.rglob("*"))) == (n, 2, "", USAGE, [], [])


def test_cli_remove_refuses_an_n_that_is_not_a_positive_whole_number_with_the_usage_line_and_runs_no_git(fake_processes, 
        monkeypatch, tmp_path, issue_worktree, run_cli):
    victim = tmp_path / ".claude" / "worktrees" / "victim"
    victim.mkdir(parents=True)
    for n in ("abc", "0", "-3", "../../.claude/worktrees/victim"):
        calls = fake_git(fake_processes, {})

        code, out, err = run_cli(issue_worktree, ["--remove", n], cwd=tmp_path)

        assert (n, code, out, err, calls, victim.is_dir()) == (n, 2, "", USAGE, [], True)


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


def test_main_remove_refuses_a_dirty_worktree_and_removes_a_clean_one_without_force_at_the_unnormalised_registry_path(fake_processes, 
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/a/../repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree /srv/other\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/x\n\n" % main_tree)
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)

    calls = routing_git(fake_processes, {listing: (0, registry, ""), status: (0, "?? stray\n", "")})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == list(remove[:3])]) == (
        2, ("", "issue-worktree: %s has uncommitted changes — refusing to remove it\n" % path), [])

    for argv in (["--remove", "7"], ["--remove", "7", "extra"]):
        calls = routing_git(fake_processes, {listing: (0, registry, ""), status: (0, "", ""),
                                          remove: (0, "removed it\n", "")})
        code = issue_worktree.main(argv)
        assert (argv, code, capsys.readouterr()[:], calls) == (
            argv, 0, ("", "removed it\n"), [list(listing), list(status), list(remove)])

    calls = routing_git(fake_processes, {listing: (0, registry, ""),
                                      status: (128, "", "fatal: cannot change to '%s'\n" % path),
                                      remove: (128, "", "fatal: '%s' is not a working tree\n" % path)})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr().out, calls) == (2, "", [list(listing), list(status), list(remove)])


def test_main_remove_returns_a_dying_gits_status_inside_0_to_3_as_it_is_and_maps_only_one_outside_to_2(fake_processes, 
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)

    calls = routing_git(fake_processes, {listing: (1, "", "error: listing failed\n")})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr().out, calls) == (1, "", [list(listing)])

    for remove_code, want in ((1, 1), (128, 2)):
        calls = routing_git(fake_processes, {listing: (0, registry, ""), status: (0, "", ""),
                                          remove: (remove_code, "", "error: remove failed\n")})
        code = issue_worktree.main(["--remove", "7"])
        assert (remove_code, code, capsys.readouterr().out, calls) == (
            remove_code, want, "", [list(listing), list(status), list(remove)])


def test_main_remove_leaves_the_snapshot_directory_outside_the_worktree_in_place_when_git_worktree_remove_fails_issue_2627(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/7"
    snapshot = tmp_path / "skill-snapshot"
    snapshot.mkdir()
    (snapshot / "status.sh").write_text("#!/bin/sh\n")
    marker = pathlib.Path(path, ".tdd", "pinned-scripts", ".snapshot-dir")
    marker.parent.mkdir(parents=True)
    marker.write_text(str(snapshot))
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)
    routing_git(fake_processes, {listing: (0, registry, ""), status: (0, "", ""),
                              remove: (128, "", "fatal: remove failed\n")})

    code = issue_worktree.main(["--remove", "7"])

    assert (code, (snapshot / "status.sh").exists()) == (2, True)


def run_worktree_of(tmp_path):
    return str(tmp_path / "repo" / ".tdd" / "wt" / "7")


def made_snapshot(directory, serving):
    """A snapshot directory as run-conductor makes one: its marker naming the worktree it serves."""
    directory.mkdir()
    (directory / "status.sh").write_text("#!/bin/sh\n")
    (directory / ".veri-snapshot").write_text(serving + "\n")
    return directory


def remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, recorded, remove_code=0):
    """`--remove 7` of a clean worktree whose .snapshot-dir holds <recorded>; answers (exit code, stderr)."""
    main_tree = str(tmp_path / "repo")
    path = run_worktree_of(tmp_path)
    record = pathlib.Path(path, ".tdd", "pinned-scripts", ".snapshot-dir")
    record.parent.mkdir(parents=True)
    record.write_text(recorded)
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)
    routing_git(fake_processes, {listing: (0, registry, ""), status: (0, "", ""), remove: (remove_code, "", "")})
    capsys.readouterr()
    code = issue_worktree.main(["--remove", "7"])
    return code, capsys.readouterr().err


def test_main_remove_deletes_the_snapshot_veri_made_for_the_worktree_once_the_worktree_is_removed(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "veri-snapshot-abc123", run_worktree_of(tmp_path))

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(snapshot))

    assert (code, err, snapshot.exists()) == (0, "", False)


def test_main_remove_deletes_a_read_only_snapshot_veri_made_for_the_worktree_leaving_no_file_of_it_3963(fake_processes,
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "veri-snapshot-abc123", run_worktree_of(tmp_path))
    (snapshot / "scripts").mkdir()
    (snapshot / "scripts" / "status.sh").write_text("#!/bin/sh\n")
    importlib.import_module("veri.pinned_scripts").make_read_only(str(snapshot))

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(snapshot))

    assert (code, err, os.path.lexists(snapshot)) == (0, "", False)


def test_main_remove_exits_2_naming_the_snapshot_when_its_removal_fails_after_the_worktree_is_gone_3963(fake_processes,
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "veri-snapshot-abc123", run_worktree_of(tmp_path))

    def fails(tree):
        raise PermissionError(13, "Permission denied", tree)
    monkeypatch.setattr(importlib.import_module("veri.pinned_scripts"), "remove_tree", fails)

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(snapshot))

    assert (code, err.startswith("issue-worktree: could not remove the snapshot %s: " % snapshot)) == (2, True), err


def refusal_of(tmp_path, snapshot):
    return "issue-worktree: %s is not a snapshot veri made for %s — left in place\n" % (
        snapshot, run_worktree_of(tmp_path))


def test_main_remove_leaves_a_snapshot_whose_marker_names_another_worktree_in_place_and_says_so(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "veri-snapshot-abc123", str(tmp_path / "repo" / ".tdd" / "wt" / "8"))

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(snapshot))

    assert (code, err, (snapshot / "status.sh").exists()) == (0, refusal_of(tmp_path, snapshot), True)


def test_main_remove_leaves_a_relative_recorded_path_in_place_even_when_it_names_a_conforming_directory_from_the_cwd(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "veri-snapshot-abc123", run_worktree_of(tmp_path))

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, "veri-snapshot-abc123")

    assert (code, err, (snapshot / "status.sh").exists()) == (0, refusal_of(tmp_path, "veri-snapshot-abc123"), True)


def test_main_remove_leaves_a_symlink_to_a_conforming_snapshot_in_place_and_says_so(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "veri-snapshot-abc123", run_worktree_of(tmp_path))
    link = tmp_path / "veri-snapshot-link"
    link.symlink_to(snapshot)

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(link))

    assert (code, err, (snapshot / "status.sh").exists(), link.is_symlink()) == (
        0, refusal_of(tmp_path, link), True, True)


def test_main_remove_leaves_two_recorded_lines_in_place_even_when_each_names_a_conforming_snapshot(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    first = made_snapshot(tmp_path / "veri-snapshot-first", run_worktree_of(tmp_path))
    second = made_snapshot(tmp_path / "veri-snapshot-second", run_worktree_of(tmp_path))
    recorded = "%s\n%s" % (first, second)

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, recorded)

    assert (code, err, (first / "status.sh").exists(), (second / "status.sh").exists()) == (
        0, refusal_of(tmp_path, recorded), True, True)


def test_main_remove_of_an_empty_snapshot_record_deletes_nothing_in_the_cwd_and_prints_nothing(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    stray = made_snapshot(tmp_path / "veri-snapshot-stray", run_worktree_of(tmp_path))
    (tmp_path / ".veri-snapshot").write_text(run_worktree_of(tmp_path) + "\n")

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, "")

    assert (code, err, (stray / "status.sh").exists(), (tmp_path / ".veri-snapshot").exists()) == (0, "", True, True)


def test_main_remove_leaves_a_marked_directory_whose_name_lacks_the_veri_snapshot_prefix_in_place_and_says_so(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = made_snapshot(tmp_path / "work-dir", run_worktree_of(tmp_path))

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(snapshot))

    assert (code, err, (snapshot / "status.sh").exists()) == (0, refusal_of(tmp_path, snapshot), True)


def test_main_remove_of_a_recorded_snapshot_already_gone_prints_nothing(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    gone = tmp_path / "veri-snapshot-gone"

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(gone))

    assert (code, err) == (0, "")


def test_main_remove_leaves_a_recorded_directory_holding_no_marker_in_place_and_says_so_with_the_removals_own_exit_code(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    snapshot = tmp_path / "tmpa1b2c3"
    snapshot.mkdir()
    (snapshot / "precious.txt").write_text("not veri's\n")

    code, err = remove_run_recording(tmp_path, fake_processes, capsys, issue_worktree, str(snapshot))

    assert (code, err, (snapshot / "precious.txt").exists()) == (0, refusal_of(tmp_path, snapshot), True)


def test_main_hands_back_a_registered_worktree_whose_pid_file_holds_0_or_00_issue_819(fake_processes, 
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
        calls = routing_git(fake_processes, {listing: (0, registry, "")})
        code = issue_worktree.main(["7", "slug"])
        assert (content, code, capsys.readouterr()[:], calls) == (content, 0, (path + "\n", ""), [list(listing)])


def test_main_hands_back_a_registered_worktree_whose_pid_file_open_cannot_read_issue_965(fake_processes, 
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
    calls = routing_git(fake_processes, {listing: (0, registry, "")})
    code = issue_worktree.main(["7", "slug"])
    assert (code, capsys.readouterr()[:], calls) == (0, (path + "\n", ""), [list(listing)])


def test_main_refuses_a_branch_any_registry_entry_has_checked_out_the_main_working_tree_included_before_any_cut(fake_processes, 
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
        calls = routing_git(fake_processes, {listing: (0, registry, "")})
        code = issue_worktree.main(["5", "x"])
        assert (holder, code, capsys.readouterr()[:], calls) == (holder, 2, ("", owned % holder), [list(listing)])


def test_main_checks_out_a_local_branch_and_maps_a_dying_add_to_2(fake_processes, 
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = f"{main_tree}/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    checkout = ("git", "worktree", "add", "-q", path, "tdd/7-slug")

    for add_code, want, out in ((0, 0, path + "\n"), (128, 2, "")):
        calls = routing_git(fake_processes, {listing: (0, registry, ""), local: (0, "", ""),
                                          checkout: (add_code, "Preparing worktree\n", "")})
        code = issue_worktree.main(["7", "slug"])
        assert (add_code, code, capsys.readouterr()[:], calls) == (
            add_code, want, (out, "Preparing worktree\n"), [list(listing), list(local), list(checkout)])


def test_main_refuses_a_fresh_run_whose_fetched_branch_origin_still_holds_and_adds_no_worktree_issue_1734(fake_processes, 
        monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    main_tree = "/srv/repo"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")

    calls = routing_git(fake_processes, {
        listing: (0, registry, ""), local: (1, "", ""), remote: (0, "", ""),
        claims: (0, "1111111111111111111111111111111111111111\trefs/heads/tdd/7-slug\n", "")})
    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == ["git", "worktree", "add"]]) == (
        2, ("", "issue-worktree: tdd/7-slug is already on origin — another run holds it;"
                " to take it over run: issue-worktree.sh --take-over 7 slug\n"), [])


def test_main_take_over_cuts_the_worktree_on_a_local_branch_from_origins_branch_another_run_holds_4080(fake_processes,
        monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    main_tree = "/srv/repo"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")
    fetch = ("git", "fetch", "-q", "origin", "+refs/heads/tdd/7-slug:refs/remotes/origin/tdd/7-slug")
    adopt = ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", "/srv/repo/.tdd/wt/7", "origin/tdd/7-slug")

    calls = routing_git(fake_processes, {
        listing: (0, registry, ""), local: (1, "", ""), remote: (0, "", ""), fetch: (0, "", ""),
        claims: (0, "1111111111111111111111111111111111111111\trefs/heads/tdd/7-slug\n", ""), adopt: (0, "", "")})
    code = issue_worktree.main(["--take-over", "7", "slug"])

    assert (code, capsys.readouterr().out, [c for c in calls if c[:2] == ["git", "fetch"] or c[:3] == ["git", "worktree", "add"]]) == (
        0, "/srv/repo/.tdd/wt/7\n", [list(fetch), list(adopt)])


def test_main_take_over_with_no_remote_tracking_ref_asks_origin_then_fetches_and_cuts_4080(fake_processes,
        monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    registry = "worktree /srv/repo\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
    fetch = ("git", "fetch", "-q", "origin", "+refs/heads/tdd/7-slug:refs/remotes/origin/tdd/7-slug")
    adopt = ("git", "worktree", "add", "-q", "--no-track", "-b", "tdd/7-slug", "/srv/repo/.tdd/wt/7", "origin/tdd/7-slug")
    calls = routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug"): (1, "", ""),
        ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*"): (0, "1111111\trefs/heads/tdd/7-slug\n", ""),
        fetch: (0, "", ""), adopt: (0, "", "")})
    code = issue_worktree.main(["--take-over", "7", "slug"])

    assert (code, capsys.readouterr().out, [c for c in calls if c[:2] == ["git", "fetch"] or c[:3] == ["git", "worktree", "add"]]) == (
        0, "/srv/repo/.tdd/wt/7\n", [list(fetch), list(adopt)])


def test_main_take_over_over_a_local_branch_that_differs_from_origins_after_the_fetch_exits_2_naming_both_shas_4080(
        fake_processes, monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    registry = "worktree /srv/repo\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
    local, remote = "a" * 40, "b" * 40
    calls = routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug"): (0, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug"): (0, "", ""),
        ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*"): (0, remote + "\trefs/heads/tdd/7-slug\n", ""),
        ("git", "fetch", "-q", "origin", "+refs/heads/tdd/7-slug:refs/remotes/origin/tdd/7-slug"): (0, "", ""),
        ("git", "rev-parse", "--verify", "-q", "refs/heads/tdd/7-slug"): (0, local + "\n", ""),
        ("git", "rev-parse", "--verify", "-q", "refs/remotes/origin/tdd/7-slug"): (0, remote + "\n", ""),
        ("git", "worktree", "add", "-q", "/srv/repo/.tdd/wt/7", "tdd/7-slug"): (0, "", "")})
    code = issue_worktree.main(["--take-over", "7", "slug"])

    err = capsys.readouterr().err
    assert (code, local in err and remote in err, [c for c in calls if c[:3] == ["git", "worktree", "add"]]) == (2, True, [])


def test_main_take_over_whose_fetch_of_origins_branch_gets_no_answer_exits_2_naming_the_fetch_and_adds_no_worktree_4080(
        fake_processes, monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    registry = "worktree /srv/repo\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
    calls = routing_git(fake_processes, {
        ("git", "worktree", "list", "--porcelain"): (0, registry, ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug"): (1, "", ""),
        ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug"): (0, "", ""),
        ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*"): (0, "1111111\trefs/heads/tdd/7-slug\n", ""),
        ("git", "fetch", "-q", "origin", "+refs/heads/tdd/7-slug:refs/remotes/origin/tdd/7-slug"):
            (128, "", "fatal: unable to access origin\n")})
    code = issue_worktree.main(["--take-over", "7", "slug"])

    err = capsys.readouterr().err
    assert (code, "git fetch" in err and "tdd/7-slug" in err, [c for c in calls if c[:3] == ["git", "worktree", "add"]]) == (
        2, True, [])


def test_main_cuts_a_fresh_branch_from_the_default_when_only_a_stale_remote_tracking_ref_names_the_issue_issue_1734(fake_processes,
        monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
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

    calls = routing_git(fake_processes, {
        listing: (0, registry, ""), local: (1, "", ""), remote: (0, "", ""), claims: (0, "", ""),
        symref: (0, "origin/trunk\n", ""), get_url: (0, "/srv/origin.git\n", ""),
        fetch: (0, "", ""), fresh: (0, "", ""), stale: (0, "", "")})
    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == ["git", "worktree", "add"]]) == (
        0, (path + "\n", ""), [list(fresh)])


def test_main_names_the_default_branch_from_origin_head_else_from_the_remotes_symref_and_refuses_when_neither_names_one(fake_processes, 
        monkeypatch, capsys, issue_worktree):
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_view", lambda number, field: "taken:other\n", raising=False)
    main_tree = "/srv/repo"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    local = ("git", "show-ref", "--verify", "--quiet", "refs/heads/tdd/7-slug")
    remote = ("git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/tdd/7-slug")
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    get_url = ("git", "remote", "get-url", "origin")
    ls_remote = ("git", "ls-remote", "--symref", "origin", "HEAD")
    claims = ("git", "ls-remote", "--heads", "origin", "refs/heads/tdd/7-*")
    own_refs = ("git", "for-each-ref", "--format=%(refname)", "refs/heads/tdd/7-*")
    origin_refs = ("git", "for-each-ref", "--format=%(refname)", "refs/remotes/origin/tdd/7-*")
    refusal = ("issue-worktree: cannot determine origin's default branch"
               " (no refs/remotes/origin/HEAD, and the remote did not name one)\n")
    sha = "2222222222222222222222222222222222222222"

    def run(answers):
        recorded = routing_git(fake_processes, answers)
        code = issue_worktree.main(["7", "slug"])
        calls = [tuple(c) for c in recorded]
        return code, capsys.readouterr()[:], calls

    base = {listing: (0, registry, ""), local: (1, "", ""), remote: (1, "", ""),
            get_url: (0, "/srv/origin.git\n", "url noise\n"),
            claims: (0, "", ""), own_refs: (0, "", ""), origin_refs: (0, "", "")}
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
        assert (label, sorted(set(before) - {ls_remote})) == (label, sorted({listing, local, remote, symref, get_url, claims, own_refs, origin_refs}))

    unnamed = (
        ("no ref: line", (0, "%s\tHEAD\n" % sha, "ls noise\n")),
        ("unreachable", (128, "", "fatal: could not read from remote repository\n")),
        ("outside refs/heads", (0, "ref: refs/tags/v1\tHEAD\n%s\tHEAD\n" % sha, "")),
    )
    for label, answer in unnamed:
        code, captured, calls = run({**base, symref: (1, "", "symref noise\n"), ls_remote: answer})
        assert (label, code, captured, calls[-1], sorted(calls)) == (
            label, 2, ("", refusal), ls_remote, sorted([listing, local, remote, symref, get_url, claims, own_refs, origin_refs, ls_remote]))


def test_main_falls_back_to_a_local_main_then_master_only_without_an_origin_remote_and_refuses_when_neither_exists(fake_processes, 
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
        recorded = routing_git(fake_processes, {**base, main: (main_code, "", ""), master: (master_code, "", "")})
        code = issue_worktree.main(["7", "slug"])
        calls = [tuple(c) for c in recorded]
        adds = [c for c in calls if c[1:3] == ("worktree", "add")]
        assert (label, code, capsys.readouterr()[:], adds[-1] if adds else None,
                [c for c in calls if c[1] in ("fetch", "ls-remote")]) == (label, *want, [])


def test_default_branch_name_answers_the_same_name_and_message_from_origin_head_from_origin_and_from_a_local_main_or_master_4042(
        fake_processes, issue_worktree):
    symref = ("git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    ls_remote = ("git", "ls-remote", "--symref", "origin", "HEAD")
    main = ("git", "show-ref", "--verify", "--quiet", "refs/heads/main")
    master = ("git", "show-ref", "--verify", "--quiet", "refs/heads/master")
    unset = (1, "", "fatal: ref refs/remotes/origin/HEAD is not a symbolic ref\n")
    origin_message = "cannot determine origin's default branch (no refs/remotes/origin/HEAD, and the remote did not name one)"
    cases = {
        "origin/HEAD set": ("/srv/origin.git\n", {symref: (0, "origin/trunk\n", "")}),
        "origin names a branch": ("/srv/origin.git\n", {symref: unset, ls_remote: (0, "ref: refs/heads/develop\tHEAD\n", "")}),
        "origin names none": ("/srv/origin.git\n", {symref: unset, ls_remote: (0, "2222\tHEAD\n", "")}),
        "no origin, local main": (None, {symref: unset, main: (0, "", ""), master: (0, "", "")}),
        "no origin, local master": (None, {symref: unset, main: (1, "", ""), master: (0, "", "")}),
        "no origin, neither": (None, {symref: unset, main: (1, "", ""), master: (1, "", "")}),
    }
    answered = {}
    for label, (origin, answers) in cases.items():
        routing_git(fake_processes, answers)
        answered[label] = issue_worktree.default_branch_name(origin)

    assert answered == {
        "origin/HEAD set": ("trunk", None),
        "origin names a branch": ("develop", origin_message),
        "origin names none": ("", origin_message),
        "no origin, local main": ("main", None),
        "no origin, local master": ("master", None),
        "no origin, neither": ("", "cannot determine the default branch (no origin/HEAD, no local main or master)"),
    }


def test_main_cuts_from_a_fetched_origin_default_with_no_track_and_refuses_to_cut_from_a_stale_one_when_the_fetch_fails(fake_processes,
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

    recorded = routing_git(fake_processes, {**base, fetch: (0, "fetched\n", "")})
    code = issue_worktree.main(["7", "slug"])
    assert (code, capsys.readouterr()[:], [tuple(c) for c in recorded][-2:]) == (0, (path + "\n", "fetched\n"), [fetch, add])

    recorded = routing_git(fake_processes, {**base, fetch: (1, "", "fatal: couldn't find remote ref trunk\n")})
    code = issue_worktree.main(["7", "slug"])
    out, err = capsys.readouterr()
    assert (code, out, err[-len(refusal):], [tuple(c) for c in recorded if c[1:3] == ["worktree", "add"]]) == (
        2, "", refusal, [])


def test_main_answers_each_ls_remote_shape_with_its_stdout_stderr_and_exit_code_when_origin_head_is_unset(fake_processes, 
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
        routing_git(fake_processes, {**base, ls_remote: answer})
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
    monkeypatch.setattr(issue_worktree.github, "gh_json", fake_gh_json)
    return issue_worktree.claiming_pr("62", "https://github.com/o/r.git"), asked


def test_claiming_pr_1656_asks_github_for_a_github_com_origin_and_names_the_open_pr_that_closes_the_issue_not_one_listed_before_it(issue_worktree, monkeypatch):
    prs = [{"isCrossRepository": False, "state": "OPEN", "body": "Closes #63", "url": "https://github.com/o/r/pull/10"},
           {"isCrossRepository": False, "state": "OPEN", "body": "Fixes it.\n\nCloses #62", "url": "https://github.com/o/r/pull/9"}]

    assert _open_prs(issue_worktree, monkeypatch, prs) == ("https://github.com/o/r/pull/9", ["prs.json"])


def test_claiming_pr_1656_names_no_pr_on_a_github_com_origin_when_the_only_open_one_closes_another_issue(issue_worktree, monkeypatch):
    prs = [{"isCrossRepository": False, "state": "OPEN", "body": "Closes #63", "url": "https://github.com/o/r/pull/10"}]

    assert _open_prs(issue_worktree, monkeypatch, prs) == ("", ["prs.json"])


@pytest.mark.parametrize("fork", [{"isCrossRepository": True},
                                  {"head": {"repo": {"full_name": "stranger/r"}}, "base": {"repo": {"full_name": "o/r"}}},
                                  {"head": {"repo": None}, "base": {"repo": {"full_name": "o/r"}}},
                                  {}])
def test_claiming_pr_3974_names_no_pr_whose_head_is_in_another_repository(issue_worktree, monkeypatch, fork):
    # A fork's PR, which anyone can open, saying Closes #62 must not stop a run of #62 (PRD 022.15, CW1).
    prs = [dict(fork, state="OPEN", body="Closes #62", url="https://github.com/o/r/pull/9")]

    assert _open_prs(issue_worktree, monkeypatch, prs) == ("", ["prs.json"])


def test_main_remove_still_succeeds_when_the_recorded_snapshot_directory_is_already_gone_issue_2627(fake_processes, 
        tmp_path, monkeypatch, capsys, issue_worktree):
    main_tree = str(tmp_path / "repo")
    path = f"{main_tree}/.tdd/wt/7"
    marker = pathlib.Path(path, ".tdd", "pinned-scripts", ".snapshot-dir")
    marker.parent.mkdir(parents=True)
    marker.write_text(str(tmp_path / "already-gone"))
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)
    routing_git(fake_processes, {listing: (0, registry, ""), status: (0, "", ""), remove: (0, "", "")})

    code = issue_worktree.main(["--remove", "7"])

    assert (code, capsys.readouterr().out) == (0, "")


def test_the_escape_guard_fails_a_case_whose_subject_runs_git_from_the_repository_the_tests_live_in_not_its_scratch_repository(
        monkeypatch, issue_worktree):
    monkeypatch.chdir(pathlib.Path(__file__).resolve().parents[5])

    with pytest.raises(AssertionError, match="starts git against the repository the tests live in"):
        issue_worktree.main(["7", "slug"])


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path, monkeypatch, issue_worktree, capsys):
    import importlib.util
    real = pathlib.Path(issue_worktree.__file__).resolve()
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(real, farm / "issue_worktree.py")
    spec = importlib.util.spec_from_file_location("symlinked_issue_worktree", farm / "issue_worktree.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    monkeypatch.chdir(real.parent.parent)

    assert (loaded.main(["7", "slug"]), capsys.readouterr()) == (2, ("", "issue-worktree: type this from the repository the issue belongs to, not from the skill's own scripts directory\n"))

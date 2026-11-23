"""In-process cases for veri/stack_land.py, the module stack-land.sh is a shim over (PRD 034.4a): the stack branch
stack-branch.sh names (stack_branch.named) and the sibling scripts it runs (stack_fix.script) are injected in-process,
so no case starts a process."""
import importlib
import json
import os
import re
import subprocess

import pytest


@pytest.fixture
def stack_land():
    return importlib.import_module("veri.stack_land")


class World:
    """What stack_branch.named answers, and every sibling script run; <answers> maps a script's name to its (exit code,
    stdout), (0, "") for one it does not name. git (git.out) names <default> as origin's default branch and answers
    <ahead> to `rev-list --count`; GitHub (github.gh_api) lists <onto>, the open pull requests as REST records, and
    reads every pull request as merged and every issue as closed, save those numbered in <open_issues>. origin
(git.network, its calls kept in <network>) fetches and pushes, and its heads are <heads>, a branch name to its commit.
GitHub opens a pull request (github.pr_open, each kept in <opened> as (head, base), its body in <bodies>) at <opens>, its
url; every other gh command (github.run_gh) is kept in <gh>, each answering 0. `git log` of a range from origin/<default> answers <subjects>; the pull requests merged into a base (github.merged_pulls) are <merged>,
(number, body) pairs from this repository. origin/<default> is an ancestor of the cut (`merge-base --is-ancestor`) when
<ancestor>; a worktree added, its rebase, and `rev-parse HEAD` in it answer, the last <rebased>, save that the rebase onto
origin/<default> fails with a conflict when <rebase_conflict>. `git log` of that range asking for the Veri-Suite trailer
answers <suites>. Every git, script and gh
call is also kept, in order, in <log>: ("git", *args), (script, *args) and ("gh", *args)."""

    def __init__(self, monkeypatch, named, answers=None, default="trunk", ahead=0, onto=(), heads=None,
                 opens="https://github.com/owner/repo/pull/90", subjects="", merged=(), open_issues=(), ancestor=True,
                 rebased=None, rebase_conflict=False, suites=""):
        self.scripts, self.network, self.opened, self.bodies, self.gh, self.log = [], [], [], [], [], []
        self.limits = []  # (script, the bound it ran under, None for none), one per script run
        heads = heads or {}
        answers = answers or {}
        stack_branch = importlib.import_module("veri.stack_branch")
        git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")

        def out(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:2] == ("merge-base", "--is-ancestor"):
                if ancestor:
                    return ""
                raise git.GitFailed(args, 1, "")
            if rebase_conflict and args[-2:] == ("rebase", "origin/" + default):
                raise git.GitFailed(args, 1, "CONFLICT (content): Merge conflict in a.txt\n")
            if "worktree" in args or "rebase" in args:
                return ""
            if args[-2:] == ("rev-parse", "HEAD"):
                return rebased
            if args[:1] == ("symbolic-ref",):
                return "origin/" + default
            if args[:2] == ("rev-list", "--count"):
                return str(ahead)
            if args[:1] == ("log",) and any("Veri-Suite" in arg for arg in args):
                return suites
            if args[:1] == ("log",) and any(arg.startswith("origin/%s.." % default) for arg in args):
                return subjects
            raise git.GitFailed(args, 128, "not faked")

        def gh_api(path, stderr=None):
            issue = re.fullmatch(r"repos/[^/]+/[^/]+/issues/(\d+)", path)
            if issue:
                said = {"state": "open" if int(issue[1]) in open_issues else "closed"}
                return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")
            said = {"state": "closed", "merged": True} if re.fullmatch(r"repos/[^/]+/[^/]+/pulls/\d+", path) else list(onto)
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")

        def network(*args, cwd=None):
            self.network.append(args)
            self.log.append(("git",) + args)
            said = ""
            if args[:1] == ("ls-remote",):
                said = "".join("%s\trefs/heads/%s\n" % (sha, name) for name, sha in heads.items()
                               if "refs/heads/" + name in args)
            return subprocess.CompletedProcess(["git", *args], 0, said, "")

        monkeypatch.setattr(git, "out", out)
        monkeypatch.setattr(git, "network", network)
        def pr_open(head, base, title, body):
            self.opened.append((head, base))
            self.bodies.append(body)
            return opens

        monkeypatch.setattr(github, "gh_api", gh_api)
        monkeypatch.setattr(github, "pr_open", pr_open)
        monkeypatch.setattr(github, "run_gh", lambda *args, stderr=None: (
            self.gh.append(("gh",) + args) or self.log.append(("gh",) + args)
            or subprocess.CompletedProcess(["gh", *args], 0, "", "")))
        monkeypatch.setattr(github, "merged_pulls", lambda base, repo=None: [github._pull(
            {"number": number, "body": body, "state": "MERGED", "baseRefName": base, "isCrossRepository": False})
            for number, body in merged])

        def answer(root):
            if isinstance(named, BaseException):
                raise named
            return named

        def script(name, *args, limit=None):
            self.limits.append((name, limit))
            self.scripts.append((name,) + args)
            self.log.append((name,) + args)
            return answers.get(name, (0, ""))

        monkeypatch.setattr(stack_branch, "named", answer)
        monkeypatch.setattr(importlib.import_module("veri.stack_fix"), "script", script)


LINE = "CLAUDE.md: the line 'veri: stack branch:' names no branch"


@pytest.mark.parametrize("named, said", [
    (None, "stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch"),
    ("refused", "stack-branch.sh exits 2: " + LINE),
])
def test_exits_2_naming_stack_branch_sh_exit_and_its_stderr_line_when_it_does_not_exit_0_running_nothing_after_it(
        monkeypatch, run_cli, stack_land, named, said):
    refused = importlib.import_module("veri.stack_branch").Refused(LINE) if named == "refused" else named
    world = World(monkeypatch, refused)

    code, out, err = run_cli(stack_land, [])

    assert (code, out, err.count("\n"), said in err, world.scripts) == (2, "", 1, True, []), err


def test_a_red_stack_exits_1_naming_the_red_commit_and_its_runs_url_running_nothing_after_stack_red_sh(
        monkeypatch, run_cli, stack_land):
    red, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/actions/runs/4242"
    world = World(monkeypatch, "stack", {"stack-red.sh": (0, "%s %s failure\n" % (red, url))})

    code, out, err = run_cli(stack_land, [])

    assert (code, out, red in err, url in err, world.scripts) == (1, "", True, True, [("stack-red.sh",)]), err


def test_stack_red_sh_exiting_2_exits_2_running_nothing_after_it(monkeypatch, run_cli, stack_land):
    world = World(monkeypatch, "stack", {"stack-red.sh": (2, "")})

    code, out, err = run_cli(stack_land, [])

    assert (code, out, world.scripts) == (2, "", [("stack-red.sh",)]), err


def test_on_stack_red_sh_exit_3_stack_green_sh_exiting_3_exits_3_nothing_to_land_running_nothing_after_it(
        monkeypatch, run_cli, stack_land):
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (3, "")})

    code, out, err = run_cli(stack_land, [])

    assert (code, out, world.scripts) == (3, "", [("stack-red.sh",), ("stack-green.sh",)]), err


def test_on_stack_red_sh_exit_3_stack_green_sh_exiting_2_exits_2_running_nothing_after_it(
        monkeypatch, run_cli, stack_land):
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (2, "")})

    code, out, err = run_cli(stack_land, [])

    assert (code, out, world.scripts) == (2, "", [("stack-red.sh",), ("stack-green.sh",)]), err


@pytest.mark.parametrize("value", ["0", "-3", "ten", "2.5"])
def test_a_veri_slice_commits_that_is_not_a_whole_number_of_1_or_more_exits_2_naming_it_before_any_lock_or_write(
        monkeypatch, run_cli, stack_land, value):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")})

    code, out, err = run_cli(stack_land, ["--now"], env={"VERI_SLICE_COMMITS": value})

    past_the_reads = [ran for ran in world.scripts if ran[0] not in ("stack-red.sh", "stack-green.sh")]
    assert (code, out, "VERI_SLICE_COMMITS" in err, value in err, past_the_reads) == (2, "", True, True, []), err


def test_a_cut_fewer_than_veri_slice_commits_ahead_on_a_stack_a_pull_request_is_open_onto_exits_3_saying_the_count_and_what_is_live_taking_no_lock(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/77"
    repo = {"full_name": "owner/repo"}
    live = {"number": 77, "html_url": url, "head": {"ref": "issue-77", "repo": repo}, "base": {"ref": "stack", "repo": repo}}
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  onto=[live])

    code, out, err = run_cli(stack_land, [])

    assert (code, out, "7 commits" in err, url in err, world.scripts) == (
        3, "", True, True, [("stack-red.sh",), ("stack-green.sh",)]), err


@pytest.mark.parametrize("head_repo", [{"full_name": "someone/fork"}, None])
def test_a_pull_request_onto_the_stack_from_another_repository_keeps_nothing_live_and_an_idle_stack_takes_the_merge_lock(
        monkeypatch, run_cli, stack_land, head_repo):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/77"
    fork = {"number": 77, "html_url": url, "head": {"ref": "issue-77", "repo": head_repo},
            "base": {"ref": "stack", "repo": {"full_name": "owner/repo"}}}
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "merge-lock.sh": (2, "")}, ahead=7, onto=[fork])
    monkeypatch.setattr(importlib.import_module("veri.event"), "journals", lambda who="status.sh": iter([]))

    code, out, err = run_cli(stack_land, [])

    assert ([ran[:3] for ran in world.scripts], url in err) == (
        [("stack-red.sh",), ("stack-green.sh",), ("merge-lock.sh", "take", "--pid")], False), err


def test_a_cut_fewer_than_veri_slice_commits_ahead_with_no_pull_request_onto_the_stack_and_a_journal_naming_a_living_conductor_exits_3_saying_the_count_and_that_conductor_taking_no_lock(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)
    event, pid_file = importlib.import_module("veri.event"), importlib.import_module("veri.pid_file")
    dead, alive = {"event": "conductor-start", "pid": "111"}, {"event": "conductor-start", "pid": "4242"}
    monkeypatch.setattr(event, "journals", lambda who="status.sh": iter([
        ("/journals/90.jsonl", [dead]),
        ("/journals/4318.jsonl", [dead, {"event": "launch"}, alive, {"event": "launch"}]),
    ]))
    monkeypatch.setattr(pid_file, "conductor_alive", lambda start: start["pid"] == "4242")

    code, out, err = run_cli(stack_land, [])

    assert (code, out, "7 commits" in err, "#4318" in err, "#90" in err, world.scripts) == (
        3, "", True, True, False, [("stack-red.sh",), ("stack-green.sh",)]), err


@pytest.mark.parametrize("size, ahead", [(None, 100), (None, 250), ("5", 5)])
def test_a_cut_veri_slice_commits_or_more_ahead_goes_on_to_take_the_merge_lock_though_a_pull_request_is_open_onto_the_stack(
        monkeypatch, run_cli, stack_land, size, ahead):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/77"
    repo = {"full_name": "owner/repo"}
    live = {"number": 77, "html_url": url, "head": {"ref": "issue-77", "repo": repo}, "base": {"ref": "stack", "repo": repo}}
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "merge-lock.sh": (2, "")}, ahead=ahead, onto=[live])

    code, out, err = run_cli(stack_land, [], env={} if size is None else {"VERI_SLICE_COMMITS": size})

    assert [ran[:3] for ran in world.scripts] == [
        ("stack-red.sh",), ("stack-green.sh",), ("merge-lock.sh", "take", "--pid")], err


def test_a_cut_fewer_than_veri_slice_commits_ahead_on_an_idle_stack_goes_on_to_take_the_merge_lock(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "merge-lock.sh": (2, "")}, ahead=7)
    event, pid_file = importlib.import_module("veri.event"), importlib.import_module("veri.pid_file")
    dead = {"event": "conductor-start", "pid": "111"}
    monkeypatch.setattr(event, "journals", lambda who="status.sh": iter([("/journals/90.jsonl", [dead, {"event": "launch"}])]))
    monkeypatch.setattr(pid_file, "conductor_alive", lambda start: False)

    code, out, err = run_cli(stack_land, [])

    assert [ran[:3] for ran in world.scripts] == [
        ("stack-red.sh",), ("stack-green.sh",), ("merge-lock.sh", "take", "--pid")], err


def test_with_now_a_cut_fewer_than_veri_slice_commits_ahead_on_a_live_stack_still_goes_on_to_take_the_merge_lock(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/77"
    repo = {"full_name": "owner/repo"}
    live = {"number": 77, "html_url": url, "head": {"ref": "issue-77", "repo": repo}, "base": {"ref": "stack", "repo": repo}}
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "merge-lock.sh": (2, "")}, ahead=7, onto=[live])

    code, out, err = run_cli(stack_land, ["--now"])

    assert [ran[:3] for ran in world.scripts] == [
        ("stack-red.sh",), ("stack-green.sh",), ("merge-lock.sh", "take", "--pid")], err


def test_a_failed_merge_lock_sh_take_exits_2_with_nothing_fetched_pushed_or_opened(monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "merge-lock.sh": (2, "")}, ahead=7)
    writes = []
    git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")
    for module, name in [(git, "git"), (git, "network"), (github, "run_gh"), (github, "pr_open"),
                         (github, "gh_pr_create")]:
        monkeypatch.setattr(module, name, lambda *args, _name=name, **kwargs: writes.append((_name,) + args))

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code, out, "merge-lock.sh" in err, writes, world.scripts[-1][:2]) == (
        2, "", True, [], ("merge-lock.sh", "take")), err


def test_after_the_lock_is_taken_a_failed_fetch_exits_2_and_frees_the_merge_lock(monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)
    git = importlib.import_module("veri.git")

    def network(*args, **kwargs):
        if "fetch" in args:
            return subprocess.CompletedProcess(["git", *args], 128, "", "fatal: unable to access origin\n")
        raise AssertionError("network call after the failed fetch: %r" % (args,))

    monkeypatch.setattr(git, "network", network)

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code, out, "fetch" in err, [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_after_the_fetch_creates_the_slice_branch_named_after_the_first_10_characters_of_the_cut_at_the_cut_on_origin(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)
    git, calls = importlib.import_module("veri.git"), []

    def network(*args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(["git", *args], 0, "", "")

    monkeypatch.setattr(git, "network", network)

    code, out, err = run_cli(stack_land, ["--now"])

    pushes = [args for args in calls if args[:1] == ("push",)]
    assert [("origin" in args, cut + ":refs/heads/stack-slice-3f2a9c1d0b" in args) for args in pushes] == [
        (True, True)], (calls, err)
    assert calls.index(pushes[0]) > calls.index(("fetch", "--prune", "origin")), calls


def test_a_branch_of_the_slice_name_already_on_origin_at_another_commit_exits_2_naming_it_nothing_pushed_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut, other = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  heads={"stack-slice-3f2a9c1d0b": other})

    code, out, err = run_cli(stack_land, ["--now"])

    pushes = [args for args in world.network if args[:1] == ("push",)]
    assert (code, out, "stack-slice-3f2a9c1d0b" in err, other in err, pushes,
            [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, True, [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_a_failed_ls_remote_of_the_slice_branch_exits_2_naming_the_read_nothing_pushed_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)
    git = importlib.import_module("veri.git")
    faked = git.network

    def network(*args, **kwargs):
        if args[:1] == ("ls-remote",):
            world.network.append(args)
            return subprocess.CompletedProcess(["git", *args], 128, "", "fatal: unable to access origin\n")
        return faked(*args, **kwargs)

    monkeypatch.setattr(git, "network", network)

    code, out, err = run_cli(stack_land, ["--now"])

    pushes = [args for args in world.network if args[:1] == ("push",)]
    assert (code, out, "ls-remote" in err, pushes, [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_a_branch_of_the_slice_name_already_on_origin_at_the_cut_itself_is_kept_and_stack_land_goes_on_not_a_refusal(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  heads={"stack-slice-3f2a9c1d0b": cut})

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code != 2, "already on origin" in err, [ran[:2] for ran in world.scripts if ran[0] == "merge-lock.sh"]) == (
        True, False, [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_a_failed_push_of_the_slice_branch_exits_2_naming_the_branch_nothing_opened_or_merged_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)
    git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")
    faked, writes = git.network, []

    def network(*args, **kwargs):
        if args[:1] == ("push",):
            world.network.append(args)
            return subprocess.CompletedProcess(["git", *args], 1, "", "error: failed to push some refs\n")
        return faked(*args, **kwargs)

    monkeypatch.setattr(git, "network", network)
    for name in ("run_gh", "pr_open", "gh_pr_create"):
        monkeypatch.setattr(github, name, lambda *args, _name=name, **kwargs: writes.append((_name,) + args))

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code, out, "stack-slice-3f2a9c1d0b" in err, writes, [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_opens_a_ready_not_draft_pull_request_from_the_slice_branch_to_the_default_branch_when_none_is_open_for_that_head(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)

    code, out, err = run_cli(stack_land, ["--now"])

    assert world.opened == [("stack-slice-3f2a9c1d0b", "trunk")], err


def test_when_a_pull_request_of_the_slice_branchs_head_is_already_open_reuses_it_and_opens_none(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/88"
    repo = {"full_name": "owner/repo"}
    already = {"number": 88, "html_url": url, "state": "open", "draft": False, "title": "Land stack at 3f2a9c1d0b",
               "head": {"ref": "stack-slice-3f2a9c1d0b", "label": "owner:stack-slice-3f2a9c1d0b", "repo": repo,
                        "sha": cut},
               "base": {"ref": "trunk", "repo": repo}}
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  onto=[already])

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code != 2, world.opened) == (True, []), err


def test_the_slice_pull_requests_body_has_one_closes_line_per_issue_whose_pull_request_merged_into_the_stack_in_the_slices_range_carries_closes(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  subjects="feat: one (#11)\nrefactor: one tidied (#11)\nfeat: two (#12)\n",
                  merged=[(101, "Closes #11\n\nthe first"), (102, "Closes #12"), (103, "Closes #13, merged after the cut")])

    code, out, err = run_cli(stack_land, ["--now"])

    assert [[line for line in body.splitlines() if line.startswith("Closes")] for body in world.bodies] == [
        ["Closes #11", "Closes #12"]], err


def test_a_merged_pull_request_whose_body_reads_reverted_from_the_stack_by_gives_its_issue_no_closes_line_in_the_slice_body(
        monkeypatch, run_cli, stack_land):
    cut, revert = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  subjects="feat: one (#11)\nfeat: two (#12)\nrevert: take issue 12's commits off the stack (#12)\n",
                  merged=[(101, "Closes #11\n\nthe first"), (102, "Reverted from stack by %s\n\nthe second" % revert)])

    code, out, err = run_cli(stack_land, ["--now"])

    assert [[line for line in body.splitlines() if line.startswith("Closes")] for body in world.bodies] == [
        ["Closes #11"]], err


def test_an_issue_named_only_by_commit_subjects_in_the_slices_range_gets_no_closes_line_and_is_named_on_stderr(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  subjects="feat: one (#11)\nfix: pushed straight to the stack (#14)\n",
                  merged=[(101, "Closes #11\n\nthe first")])

    code, out, err = run_cli(stack_land, ["--now"])

    assert ([[line for line in body.splitlines() if line.startswith("Closes")] for body in world.bodies],
            [line for line in err.splitlines() if "#14" in line] != [], "#11" in err) == ([["Closes #11"]], True, False), err


@pytest.mark.parametrize("failing, words", [
    ("stack_pulls", "open pull requests from stack-slice-3f2a9c1d0b"),
    ("pr_open", "opening the pull request from stack-slice-3f2a9c1d0b"),
    ("merged_pulls", "pull requests merged into stack"),
    ("merged_pulls not JSON", "pull requests merged into stack"),
    ("git log", "git log"),
])
def test_after_the_lock_is_taken_a_github_read_that_gets_no_answer_or_a_failed_git_read_exits_2_naming_it_the_merge_lock_freed_no_traceback(
        monkeypatch, run_cli, stack_land, failing, words):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  subjects="feat: one (#11)\n")
    git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")
    faked = git.out

    def no_answer(*args, **kwargs):
        raise github.NoAnswer("", "HTTP 502 Bad Gateway")

    def not_json(*args, **kwargs):
        raise ValueError("Expecting value: line 1 column 1 (char 0)")

    def out(*args, **kwargs):
        if args[:1] == ("log",):
            raise git.GitFailed(args, 128, "fatal: bad revision")
        return faked(*args, **kwargs)

    if failing == "git log":
        monkeypatch.setattr(git, "out", out)
    elif failing == "merged_pulls not JSON":
        monkeypatch.setattr(github, "merged_pulls", not_json)
    else:
        monkeypatch.setattr(github, failing, no_answer)

    code, out_, err = run_cli(stack_land, ["--now"])

    assert (code, out_, words in err, "Traceback" in err, [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, False, [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def merge_calls(url, head):
    return [[("gh", "pr", "merge", url, "--rebase", "--match-head-commit", head)],
            [("gh", "api", "-X", "PUT", "repos/owner/repo/pulls/90/merge", "-f", "merge_method=rebase",
              "-f", "sha=%s" % head)]]


def test_with_origin_default_an_ancestor_of_the_cut_merges_the_slice_pull_request_with_exactly_gh_pr_merge_rebase_match_head_commit_and_no_other_flag(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)

    code, out, err = run_cli(stack_land, ["--now"], env={"VERI_GH_DRIVER": "rest"})

    assert world.gh in merge_calls(url, cut), err


def test_4665_with_the_graphql_driver_and_a_gh_refusing_every_pr_merge_with_a_403_the_land_merges_over_rest_at_the_cut_and_exits_0(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)
    rest_merge = ("gh", "api", "-X", "PUT", "repos/owner/repo/pulls/90/merge", "-f", "merge_method=rebase",
                  "-f", "sha=%s" % cut)
    github = importlib.import_module("veri.github")
    read = github.gh_api

    def run_gh(*args, stderr=None):
        world.gh.append(("gh",) + args)
        refused = args[:2] == ("pr", "merge")
        return subprocess.CompletedProcess(["gh", *args], 1 if refused else 0, "",
                                           "GraphQL: HTTP 403: Resource not accessible" if refused else "")

    def gh_api(path, stderr=None):
        if path == "repos/owner/repo/pulls/90" and rest_merge not in world.gh:
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps({"state": "open", "merged": False}), "")
        return read(path, stderr=stderr)

    monkeypatch.setattr(github, "run_gh", run_gh)
    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"], env={
        "VERI_GH_DRIVER": "graphql", "VERI_MERGE_SETTLE_READS": "1", "VERI_MERGE_SETTLE_SLEEP": "0"})

    assert (code, any(call[:3] == ("gh", "pr", "merge") for call in world.gh), rest_merge in world.gh) == (
        0, False, True), err


def test_4665_a_rest_merge_answering_405_with_repository_rule_violations_exits_1_with_the_rule_refusal_line_the_merge_called_once_no_settle_read_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)
    github = importlib.import_module("veri.github")
    said = "gh: Repository rule violations found (HTTP 405)"
    monkeypatch.setattr(github, "run_gh", lambda *args, stderr=None: (
        world.gh.append(("gh",) + args) or subprocess.CompletedProcess(["gh", *args], 1, "", said + "\n")))
    pull, reads = "repos/owner/repo/pulls/90", []
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path == pull:
            reads.append(path)
        return listing(path, stderr=stderr)

    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"], env={"VERI_GH_DRIVER": "graphql"})

    assert (code, out, "stack-land: the merge of %s was refused under the repository's rules (exit 1): %s; the merge lock"
            " freed, nothing retried" % (url, said) in err, len(world.gh), reads,
            [ran[:2] for ran in world.scripts[-2:]]) == (
        1, "", True, 1, [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_4665_a_rest_merge_answering_409_head_not_the_sha_sent_exits_1_naming_the_pull_request_and_the_head_mismatch_the_merge_called_once_no_settle_read_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)
    github = importlib.import_module("veri.github")
    said = "gh: Head branch was modified. Review and try the merge again. (HTTP 409)"
    monkeypatch.setattr(github, "run_gh", lambda *args, stderr=None: (
        world.gh.append(("gh",) + args) or subprocess.CompletedProcess(["gh", *args], 1, "", said + "\n")))
    pull, reads = "repos/owner/repo/pulls/90", []
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path == pull:
            reads.append(path)
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps({"state": "open", "merged": False}), "")
        return listing(path, stderr=stderr)

    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"], env={
        "VERI_GH_DRIVER": "graphql", "VERI_MERGE_SETTLE_READS": "1", "VERI_MERGE_SETTLE_SLEEP": "0"})

    assert (code, out, url in err and "head" in err.lower(), len(world.gh), reads,
            [ran[:2] for ran in world.scripts[-2:]]) == (
        1, "", True, 1, [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_a_merge_call_that_errors_without_naming_the_rules_then_a_read_of_the_pull_request_answering_merged_within_the_settle_window_is_success_the_merge_called_once(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)
    github = importlib.import_module("veri.github")
    monkeypatch.setattr(github, "run_gh", lambda *args, stderr=None: (
        world.gh.append(("gh",) + args) or subprocess.CompletedProcess(["gh", *args], 1, "", "HTTP 502: Bad Gateway\n")))
    pull, answers, reads = "repos/owner/repo/pulls/90", [{"state": "open", "merged": False},
                                                          {"state": "closed", "merged": True}], []
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != pull:
            return listing(path, stderr=stderr)
        reads.append(path)
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(answers[len(reads) - 1]), "")

    monkeypatch.setattr(github, "gh_api", gh_api)
    monkeypatch.setattr(importlib.import_module("veri.merge_common").time, "sleep", lambda seconds: None)

    code, out, err = run_cli(stack_land, ["--now"], env={"VERI_MERGE_SETTLE_READS": "3"})

    assert (code, len(world.gh), reads, [ran[:2] for ran in [ran for ran in world.scripts if ran[0] == "merge-lock.sh"][-2:]]) == (
        0, 1, [pull, pull], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_a_pull_request_not_reading_merged_by_the_end_of_the_settle_window_exits_2_naming_the_last_state_read_the_merge_called_once_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)
    github = importlib.import_module("veri.github")
    monkeypatch.setattr(github, "run_gh", lambda *args, stderr=None: (
        world.gh.append(("gh",) + args) or subprocess.CompletedProcess(["gh", *args], 1, "", "HTTP 502: Bad Gateway\n")))
    pull, answers, reads = "repos/owner/repo/pulls/90", [{"state": "open", "merged": False},
                                                          {"state": "closed", "merged": False}], []
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != pull:
            return listing(path, stderr=stderr)
        reads.append(path)
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(answers[len(reads) - 1]), "")

    monkeypatch.setattr(github, "gh_api", gh_api)
    monkeypatch.setattr(importlib.import_module("veri.merge_common").time, "sleep", lambda seconds: None)

    code, out, err = run_cli(stack_land, ["--now"], env={"VERI_MERGE_SETTLE_READS": "2"})

    assert (code, out, url in err, "'closed'" in err, "'open'" in err, "Traceback" in err, len(world.gh), reads,
            [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, True, False, False, 1, [pull, pull], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


@pytest.mark.parametrize("name, value", [("VERI_MERGE_SETTLE_READS", "0"), ("VERI_MERGE_SETTLE_READS", "ten"),
                                         ("VERI_MERGE_SETTLE_SLEEP", "-1"), ("VERI_MERGE_SETTLE_SLEEP", "soon")])
def test_an_unusable_settle_window_tunable_exits_2_naming_it_before_any_script_runs(
        monkeypatch, run_cli, stack_land, name, value):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)

    code, out, err = run_cli(stack_land, ["--now"], env={name: value})

    assert (code, out, name in err, value in err, world.scripts) == (2, "", True, True, []), err


def test_on_a_landing_exits_0_printing_the_slice_pull_requests_url_the_merge_commit_and_the_issues_closed_then_carries_the_stack_with_stack_carry_sh_at_the_cut_the_lock_freed_first(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    landed = "0a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, subjects="feat: one (#11)\nfeat: two (#12)\n",
                  merged=[(101, "Closes #11\n\nthe first"), (102, "Closes #12\n\nthe second")])
    github = importlib.import_module("veri.github")
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != "repos/owner/repo/pulls/90":
            return listing(path, stderr=stderr)
        said = {"state": "closed", "merged": True, "merge_commit_sha": landed, "body": world.bodies[-1]}
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")

    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code, out.splitlines(), [ran[:2] for ran in world.scripts[-4:]]) == (
        0, ["pull request: " + url, "merge commit: " + landed, "issues closed: #11 #12"],
        [("merge-lock.sh", "take"), ("merge-lock.sh", "release"), ("stack-carry.sh", cut), ("stack-tag.sh", url)]), err


@pytest.mark.parametrize("tagged, code", [((0, "v0.2 #11 c1\n"), 0), ((3, ""), 0), ((2, ""), 2), ((1, ""), 2)])
def test_after_a_landing_stack_tag_sh_runs_on_the_slice_and_an_exit_but_0_or_3_is_exit_2_naming_the_command_owed(
        monkeypatch, run_cli, stack_land, tagged, code):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "stack-tag.sh": tagged}, ahead=7, opens=url, subjects="feat: one (#11)\n",
                  merged=[(101, "Closes #11\n")])
    github = importlib.import_module("veri.github")
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != "repos/owner/repo/pulls/90":
            return listing(path, stderr=stderr)
        said = {"state": "closed", "merged": True, "merge_commit_sha": cut, "body": world.bodies[-1]}
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")

    monkeypatch.setattr(github, "gh_api", gh_api)

    said, out, err = run_cli(stack_land, ["--now"])

    owed = [line for line in err.splitlines() if "stack-tag.sh %s" % url in line and "landed" in line]
    assert (said, len(owed), tagged[1] in out, world.scripts[-1], world.scripts[-2]) == (
        code, 1 if code else 0, True, ("stack-tag.sh", url), ("stack-carry.sh", cut)), err


def test_an_issue_of_the_slice_bodys_closes_lines_still_open_after_the_settle_window_exits_2_naming_each_such_issue_the_landing_left_as_done(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    landed = "0a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, subjects="feat: one (#11)\nfeat: two (#12)\nfeat: three (#13)\n",
                  merged=[(101, "Closes #11\n"), (102, "Closes #12\n"), (103, "Closes #13\n")], open_issues=(11, 13))
    github = importlib.import_module("veri.github")
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != "repos/owner/repo/pulls/90":
            return listing(path, stderr=stderr)
        said = {"state": "closed", "merged": True, "merge_commit_sha": landed, "body": world.bodies[-1]}
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")

    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"])

    named = [line for line in err.splitlines() if "still open" in line]
    assert (code, out.splitlines(), len(named), [n in "".join(named) for n in ("#11", "#12", "#13")], len(world.gh),
            "Traceback" in err, [ran[:2] for ran in world.scripts[-3:]]) == (
        2, ["pull request: " + url, "merge commit: " + landed, "issues closed: #11 #12 #13"], 1, [True, False, True], 1,
        False, [("merge-lock.sh", "release"), ("stack-carry.sh", cut), ("stack-tag.sh", url)]), err


@pytest.mark.parametrize("carried, code", [(0, 0), (1, 2), (2, 2), (3, 0)])
def test_after_a_landing_a_stack_carry_sh_exit_but_0_or_3_exits_2_naming_the_landed_slice_and_the_command_owed_and_runs_it_under_no_bound(
        monkeypatch, run_cli, stack_land, carried, code):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "stack-carry.sh": (carried, "")}, ahead=7, opens=url)

    said, out, err = run_cli(stack_land, ["--now"])

    owed = [line for line in err.splitlines() if url in line and "owed: stack-carry.sh %s" % cut in line]
    assert (said, len(owed), ("stack-carry.sh", None) in world.limits) == (code, 1 if code else 0, True), err


def test_a_failed_carry_over_still_runs_stack_tag_sh_and_the_closes_check_naming_each_command_or_issue_owed(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "stack-carry.sh": (1, ""), "stack-tag.sh": (2, "")}, ahead=7, opens=url,
                  subjects="feat: one (#11)\n", merged=[(101, "Closes #11\n")], open_issues=(11,))
    github = importlib.import_module("veri.github")
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != "repos/owner/repo/pulls/90":
            return listing(path, stderr=stderr)
        said = {"state": "closed", "merged": True, "merge_commit_sha": cut, "body": world.bodies[-1]}
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")

    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"])

    landed = [line for line in err.splitlines() if line.startswith("stack-land: %s landed, but " % url)]
    assert (code, [ran[:2] for ran in world.scripts[-2:]], len(landed),
            ["owed: stack-carry.sh " + cut in "".join(landed), "run stack-tag.sh " + url in "".join(landed),
             "still open" in "".join(landed) and "#11" in "".join(landed)]) == (
        2, [("stack-carry.sh", cut), ("stack-tag.sh", url)], 3, [True, True, True]), err


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit])
def test_an_interrupt_after_the_merge_lock_was_taken_frees_the_lock_before_it_ends_the_land(
        monkeypatch, run_cli, stack_land, interrupt):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7)
    git = importlib.import_module("veri.git")

    def interrupted(*args, cwd=None):
        raise interrupt()

    monkeypatch.setattr(git, "network", interrupted)

    with pytest.raises(interrupt):
        stack_land.main(["--now"])

    assert [ran[:2] for ran in world.scripts if ran[0] == "merge-lock.sh"] == [
        ("merge-lock.sh", "take"), ("merge-lock.sh", "release")]


def test_a_landing_makes_no_tag_and_pushes_rebases_or_resets_nothing_of_the_stack_branch_only_the_slice_branch(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, subjects="feat: one (#11)\n", merged=[(101, "Closes #11\n")])
    git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")
    read, listing, argvs = git.out, github.gh_api, []

    def out(*args, cwd=None):
        argvs.append(("git",) + args)
        return read(*args, cwd=cwd)

    def run(*args, **kwargs):
        argvs.append(("git",) + args)
        return subprocess.CompletedProcess(["git", *args], 0, "", "")

    def gh_api(path, stderr=None):
        argvs.append(("gh", "api", path))
        return listing(path, stderr=stderr)

    monkeypatch.setattr(git, "out", out)
    monkeypatch.setattr(git, "git", run)
    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"])

    every = argvs + [("git",) + args for args in world.network] + world.gh + [
        ran for ran in world.scripts if ran[0] != "stack-tag.sh"]
    tagged = [argv for argv in every if argv[:2] == ("gh", "release")
              or any(re.search(r"\btags?\b|refs/tags/", arg) for arg in argv)]
    writes = [argv[1:] for argv in every if argv[:1] == ("git",)
              and argv[1] in ("push", "rebase", "reset", "tag", "update-ref", "branch", "checkout", "switch")]
    assert (code, tagged, writes) == (
        0, [], [("push", "origin", "%s:refs/heads/stack-slice-%s" % (cut, cut[:10]))]), err
    assert world.gh in merge_calls(url, cut), err


def test_with_origin_default_not_an_ancestor_of_the_cut_rebases_the_slice_branch_onto_it_pushes_it_leased_on_the_cut_waits_on_ci_at_the_new_head_and_merges_that_head(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    rebased, slice_branch = "7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b", "stack-slice-3f2a9c1d0b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, ancestor=False, rebased=rebased)

    code, out, err = run_cli(stack_land, ["--now"])

    def at(matches):
        return [i for i, argv in enumerate(world.log) if matches(argv)]

    rebase = at(lambda argv: argv[:1] == ("git",) and "rebase" in argv and argv[-1] == "origin/trunk")
    push = at(lambda argv: argv[:2] == ("git", "push") and "--force-with-lease=%s:%s" % (slice_branch, cut) in argv
              and "%s:refs/heads/%s" % (rebased, slice_branch) in argv)
    wait = at(lambda argv: argv[:1] == ("wait-ci.sh",) and url in argv and argv[-1] == rebased)
    merge = at(lambda argv: [argv] in merge_calls(url, rebased))
    assert (code, len(rebase), len(push), len(wait), len(merge)) == (0, 1, 1, 1, 1), (world.log, err)
    assert world.gh in merge_calls(url, rebased), (world.log, err)
    assert rebase[0] < push[0] < wait[0] < merge[0], world.log


def test_with_origin_default_an_ancestor_of_the_cut_rebases_nothing_pushes_nothing_leased_waits_on_no_ci_and_merges_the_cut(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, ancestor=True, rebased="7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b")

    code, out, err = run_cli(stack_land, ["--now"])

    rebased = [argv for argv in world.log if argv[:1] == ("git",) and ("rebase" in argv or "worktree" in argv)]
    leased = [argv for argv in world.log if argv[:2] == ("git", "push") and any(
        arg.startswith("--force") or arg.startswith("+") for arg in argv)]
    waited = [argv for argv in world.log if argv[:1] == ("wait-ci.sh",)]
    assert (code, rebased, leased, waited) == (0, [], [], []), (world.log, err)
    assert world.gh in merge_calls(url, cut), (world.log, err)


def test_a_rebase_conflict_exits_1_naming_it_nothing_merged_the_rebase_aborted_its_worktree_removed_the_lock_freed_the_slice_branch_and_its_pull_request_kept(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    slice_branch = "stack-slice-3f2a9c1d0b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, ancestor=False, rebase_conflict=True)

    code, out, err = run_cli(stack_land, ["--now"])

    rebase = [i for i, argv in enumerate(world.log) if argv[:1] == ("git",) and argv[-2:] == ("rebase", "origin/trunk")]
    after = world.log[rebase[0] + 1:] if rebase else []
    tree = world.log[rebase[0]][2] if rebase else None
    pushes = [argv for argv in world.network if argv[:1] == ("push",)]
    assert (code, out, "conflict" in err.lower(), slice_branch in err, url in err, "Traceback" in err) == (
        1, "", True, True, True, False), (world.log, err)
    assert (world.gh, pushes, ("git", "-C", tree, "rebase", "--abort") in after,
            ("git", "worktree", "remove", "--force", tree) in after, [ran[:2] for ran in world.scripts[-2:]]) == (
        [], [("push", "origin", "%s:refs/heads/%s" % (cut, slice_branch))], True, True,
        [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), (world.log, err)


def test_a_red_ci_answer_from_wait_ci_sh_on_the_rebased_head_exits_1_naming_it_nothing_merged_the_lock_freed_the_slice_branch_and_its_pull_request_kept(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    rebased, slice_branch = "7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b", "stack-slice-3f2a9c1d0b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "wait-ci.sh": (1, "")}, ahead=7, opens=url, ancestor=False, rebased=rebased)

    code, out, err = run_cli(stack_land, ["--now"])

    pushes = [argv for argv in world.network if argv[:1] == ("push",)]
    assert (code, out, "ci" in err.lower(), rebased in err, slice_branch in err, url in err, "Traceback" in err) == (
        1, "", True, True, True, True, False), (world.log, err)
    assert (world.gh, pushes, [ran[:2] for ran in world.scripts[-2:]]) == (
        [], [("push", "origin", "%s:refs/heads/%s" % (cut, slice_branch)),
             ("push", "--force-with-lease=%s:%s" % (slice_branch, cut), "origin",
              "%s:refs/heads/%s" % (rebased, slice_branch))],
        [("wait-ci.sh", url), ("merge-lock.sh", "release")]), (world.log, err)


def test_a_failed_leased_push_of_the_rebased_slice_branch_exits_2_naming_it_nothing_merged_the_lock_freed_the_slice_branch_and_its_pull_request_kept(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    rebased, slice_branch = "7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b", "stack-slice-3f2a9c1d0b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, ancestor=False, rebased=rebased)
    git = importlib.import_module("veri.git")
    faked = git.network

    def network(*args, **kwargs):
        if args[:1] == ("push",) and args[1].startswith("--force-with-lease="):
            world.network.append(args)
            world.log.append(("git",) + args)
            return subprocess.CompletedProcess(["git", *args], 1, "", "! [rejected] (stale info)\n")
        return faked(*args, **kwargs)

    monkeypatch.setattr(git, "network", network)

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code, out, "stale info" in err, slice_branch in err, url in err, "Traceback" in err) == (
        2, "", True, True, True, False), (world.log, err)
    assert (world.gh, [ran for ran in world.scripts if ran[0] == "wait-ci.sh"],
            [ran[:2] for ran in world.scripts[-2:]]) == (
        [], [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), (world.log, err)


def test_a_wait_ci_sh_exit_2_on_the_rebased_head_exits_2_naming_it_nothing_merged_the_lock_freed_the_slice_branch_and_its_pull_request_kept(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    rebased, slice_branch = "7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b", "stack-slice-3f2a9c1d0b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n"),
                                         "wait-ci.sh": (2, "")}, ahead=7, opens=url, ancestor=False, rebased=rebased)

    code, out, err = run_cli(stack_land, ["--now"])

    pushes = [argv for argv in world.network if argv[:1] == ("push",)]
    assert (code, out, "wait-ci.sh exits 2" in err, rebased in err, slice_branch in err, url in err,
            "Traceback" in err) == (2, "", True, True, True, True, False), (world.log, err)
    assert (world.gh, pushes, [ran[:2] for ran in world.scripts[-2:]]) == (
        [], [("push", "origin", "%s:refs/heads/%s" % (cut, slice_branch)),
             ("push", "--force-with-lease=%s:%s" % (slice_branch, cut), "origin",
              "%s:refs/heads/%s" % (rebased, slice_branch))],
        [("wait-ci.sh", url), ("merge-lock.sh", "release")]), (world.log, err)


@pytest.mark.parametrize("answers, code", [((None, {"state": "closed", "merged": True}), 0), ((None, None), 2)])
def test_a_read_of_the_pull_request_with_no_answer_in_the_settle_window_is_read_again_and_a_window_ending_unanswered_exits_2_the_lock_freed(
        monkeypatch, run_cli, stack_land, answers, code):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url)
    github = importlib.import_module("veri.github")
    monkeypatch.setattr(github, "run_gh", lambda *args, stderr=None: (
        world.gh.append(("gh",) + args) or subprocess.CompletedProcess(["gh", *args], 1, "", "HTTP 502: Bad Gateway\n")))
    pull, reads = "repos/owner/repo/pulls/90", []
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path != pull:
            return listing(path, stderr=stderr)
        reads.append(path)
        answer = answers[len(reads) - 1]
        if answer is None:
            raise github.NoAnswer("", "HTTP 502 Bad Gateway")
        return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(answer), "")

    monkeypatch.setattr(github, "gh_api", gh_api)
    monkeypatch.setattr(importlib.import_module("veri.merge_common").time, "sleep", lambda seconds: None)

    exit_code, out, err = run_cli(stack_land, ["--now"], env={"VERI_MERGE_SETTLE_READS": "2"})

    assert (exit_code, "Traceback" in err, len(world.gh), reads, [ran[:2] for ran in [ran for ran in world.scripts if ran[0] == "merge-lock.sh"][-2:]]) == (
        code, False, 1, [pull, pull], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_a_git_failure_in_the_rebase_worktree_that_is_not_a_conflict_exits_2_nothing_merged_the_lock_freed(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, ancestor=False, rebased="7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b")
    git = importlib.import_module("veri.git")
    faked = git.out

    def out(*args, cwd=None):
        if args[:2] == ("worktree", "add"):
            raise git.GitFailed(args, 128, "fatal: No space left on device\n")
        return faked(*args, cwd=cwd)

    monkeypatch.setattr(git, "out", out)

    code, out_, err = run_cli(stack_land, ["--now"])

    assert (code, out_, "worktree" in err, "Traceback" in err, world.gh, [ran[:2] for ran in world.scripts[-2:]]) == (
        2, "", True, False, [], [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


def test_an_issue_state_read_with_no_answer_after_a_landing_runs_last_the_carry_and_the_tag_run_and_exits_2_naming_the_closes_check_owed(
        monkeypatch, run_cli, stack_land):
    cut, url = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b", "https://github.com/owner/repo/pull/90"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  opens=url, subjects="feat: one (#11)\n", merged=[(101, "Closes #11\n")])
    github = importlib.import_module("veri.github")
    listing = github.gh_api

    def gh_api(path, stderr=None):
        if path == "repos/owner/repo/issues/11":
            raise github.NoAnswer("", "HTTP 502 Bad Gateway")
        if path == "repos/owner/repo/pulls/90":
            said = {"state": "closed", "merged": True, "merge_commit_sha": cut, "body": world.bodies[-1]}
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")
        return listing(path, stderr=stderr)

    monkeypatch.setattr(github, "gh_api", gh_api)

    code, out, err = run_cli(stack_land, ["--now"])

    landed = [line for line in err.splitlines() if line.startswith("stack-land: %s landed, but " % url)]
    assert (code, "Traceback" in err, [ran[:2] for ran in world.scripts[-3:]], len(landed),
            "owed: check that #11 is closed" in "".join(landed), "HTTP 502 Bad Gateway" in "".join(landed),
            [ran[:2] for ran in world.scripts if ran[0] == "merge-lock.sh"]) == (
        2, False, [("merge-lock.sh", "release"), ("stack-carry.sh", cut), ("stack-tag.sh", url)], 1, True, True,
        [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]), err


NAMED = re.compile(r"ztrange|mario|ferreira|github\.com/\w|#[0-9]+|[\"'/](main|master)\b|[\"']stack[\"']"
                   r"|ready-for-agent|refactor-owed|author-read|[\"'](priority|bug|legacy|refactor)[\"']|gates",
                   re.IGNORECASE)


def test_stack_land_merge_common_and_the_shim_name_no_repository_issue_branch_label_or_person(stack_land):
    module = importlib.import_module("veri.merge_common")
    shim = os.path.join(os.path.dirname(os.path.dirname(stack_land.__file__)), "stack-land.sh")
    named = []
    for path in (stack_land.__file__, module.__file__, shim):
        with open(path, encoding="utf-8") as f:
            named += ["%s:%d: %s" % (os.path.basename(path), n, line) for n, line in enumerate(f, 1)
                      if NAMED.search(line)]

    assert named == []


def test_while_the_outage_file_exists_it_exits_3_in_one_stderr_line_before_any_read_and_before_the_lock(
        tmp_path, monkeypatch, run_cli, stack_land):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "github-outage").write_text("")
    world = World(monkeypatch, AssertionError("stack-branch.sh was read"))

    code, out, err = run_cli(stack_land, [], cwd=tmp_path)

    assert (code, out, err.count("\n"), world.log, world.scripts) == (3, "", 1, [], []), err
    assert "outage" in err and err.startswith("stack-land: "), err


@pytest.mark.parametrize("case", ["skipped", "red", "neither"])
def test_the_slice_body_gains_a_line_per_veri_suite_skipped_commit_in_its_range_and_one_naming_stack_local_red_when_it_exists(
        tmp_path, monkeypatch, run_cli, stack_land, case):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    if case == "red":
        (tmp_path / ".tdd" / "stack-local-red").write_text("abc1234 tests/test_a.py::test_one\nmore\n")
    suites = ("1a2b3c4\x1ffeat: one\x1fpassed\n5d6e7f8\x1ffeat: two\x1fskipped opus the hardware is busy\n"
              "9a8b7c6\x1ffix: three\x1f\n") if case == "skipped" else ""
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  suites=suites)

    code, out, err = run_cli(stack_land, ["--now"], cwd=tmp_path)

    expected = {"skipped": ["Suite skipped on 5d6e7f8 feat: two: skipped opus the hardware is busy"],
                "red": [".tdd/stack-local-red exists: a local full run was red: abc1234 tests/test_a.py::test_one"],
                "neither": []}[case]
    assert world.bodies == ["".join(line + "\n" for line in expected)], err

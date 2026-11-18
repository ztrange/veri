"""In-process cases for veri/stack_land.py, the module stack-land.sh is a shim over (PRD 034.4a): the stack branch
stack-branch.sh names (stack_branch.named) and the sibling scripts it runs (stack_fix.script) are injected in-process,
so no case starts a process."""
import importlib
import json
import subprocess

import pytest


@pytest.fixture
def stack_land():
    return importlib.import_module("veri.stack_land")


class World:
    """What stack_branch.named answers, and every sibling script run; <answers> maps a script's name to its (exit code,
    stdout), (0, "") for one it does not name. git (git.out) names <default> as origin's default branch and answers
    <ahead> to `rev-list --count`; GitHub (github.gh_api) lists <onto>, the open pull requests as REST records. origin
(git.network, its calls kept in <network>) fetches and pushes, and its heads are <heads>, a branch name to its commit.
GitHub opens a pull request (github.pr_open, each kept in <opened> as (head, base), its body in <bodies>) at <opens>, its
url. `git log` of a range from origin/<default> answers <subjects>; the pull requests merged into a base (github.merged_pulls) are <merged>,
(number, body) pairs from this repository."""

    def __init__(self, monkeypatch, named, answers=None, default="trunk", ahead=0, onto=(), heads=None,
                 opens="https://github.com/owner/repo/pull/90", subjects="", merged=()):
        self.scripts, self.network, self.opened, self.bodies = [], [], [], []
        heads = heads or {}
        answers = answers or {}
        stack_branch = importlib.import_module("veri.stack_branch")
        git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")

        def out(*args, cwd=None):
            if args[:1] == ("symbolic-ref",):
                return "origin/" + default
            if args[:2] == ("rev-list", "--count"):
                return str(ahead)
            if args[:1] == ("log",) and any(arg.startswith("origin/%s.." % default) for arg in args):
                return subjects
            raise git.GitFailed(args, 128, "not faked")

        def gh_api(path, stderr=None):
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(list(onto)), "")

        def network(*args, cwd=None):
            self.network.append(args)
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
        monkeypatch.setattr(github, "merged_pulls", lambda base, repo=None: [github._pull(
            {"number": number, "body": body, "state": "MERGED", "baseRefName": base, "isCrossRepository": False})
            for number, body in merged])

        def answer(root):
            if isinstance(named, BaseException):
                raise named
            return named

        def script(name, *args, limit=None):
            self.scripts.append((name,) + args)
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
    live = {"number": 77, "html_url": url, "head": {"ref": "issue-77"}, "base": {"ref": "stack"}}
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  onto=[live])

    code, out, err = run_cli(stack_land, [])

    assert (code, out, "7 commits" in err, url in err, world.scripts) == (
        3, "", True, True, [("stack-red.sh",), ("stack-green.sh",)]), err


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
    live = {"number": 77, "html_url": url, "head": {"ref": "issue-77"}, "base": {"ref": "stack"}}
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
    live = {"number": 77, "html_url": url, "head": {"ref": "issue-77"}, "base": {"ref": "stack"}}
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


def test_a_branch_of_the_slice_name_already_on_origin_at_the_cut_itself_is_kept_and_stack_land_goes_on_not_a_refusal(
        monkeypatch, run_cli, stack_land):
    cut = "3f2a9c1d0b7e4a5f6c8d9e0f1a2b3c4d5e6f7a8b"
    world = World(monkeypatch, "stack", {"stack-red.sh": (3, ""), "stack-green.sh": (0, cut + "\n")}, ahead=7,
                  heads={"stack-slice-3f2a9c1d0b": cut})

    code, out, err = run_cli(stack_land, ["--now"])

    assert (code != 2, "already on origin" in err, [ran[:2] for ran in world.scripts if ran[0] == "merge-lock.sh"]) == (
        True, False, [("merge-lock.sh", "take")]), err


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

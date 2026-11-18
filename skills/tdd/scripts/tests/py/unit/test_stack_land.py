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
    <ahead> to `rev-list --count`; GitHub (github.gh_api) lists <onto>, the open pull requests as REST records."""

    def __init__(self, monkeypatch, named, answers=None, default="trunk", ahead=0, onto=()):
        self.scripts = []
        answers = answers or {}
        stack_branch = importlib.import_module("veri.stack_branch")
        git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")

        def out(*args, cwd=None):
            if args[:1] == ("symbolic-ref",):
                return "origin/" + default
            if args[:2] == ("rev-list", "--count"):
                return str(ahead)
            raise git.GitFailed(args, 128, "not faked")

        def gh_api(path, stderr=None):
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(list(onto)), "")

        monkeypatch.setattr(git, "out", out)
        monkeypatch.setattr(github, "gh_api", gh_api)

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
    status = importlib.import_module("veri.status")
    dead, alive = {"event": "conductor-start", "pid": "111"}, {"event": "conductor-start", "pid": "4242"}
    monkeypatch.setattr(status, "journals", lambda: iter([
        ("/journals/90.jsonl", [dead]),
        ("/journals/4318.jsonl", [dead, {"event": "launch"}, alive, {"event": "launch"}]),
    ]))
    monkeypatch.setattr(status, "conductor_alive", lambda start: start["pid"] == "4242")

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
    status = importlib.import_module("veri.status")
    dead = {"event": "conductor-start", "pid": "111"}
    monkeypatch.setattr(status, "journals", lambda: iter([("/journals/90.jsonl", [dead, {"event": "launch"}])]))
    monkeypatch.setattr(status, "conductor_alive", lambda start: False)

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

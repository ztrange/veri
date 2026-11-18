"""In-process cases for veri/stack_land.py, the module stack-land.sh is a shim over (PRD 034.4a): the stack branch
stack-branch.sh names (stack_branch.named) and the sibling scripts it runs (stack_fix.script) are injected in-process,
so no case starts a process."""
import importlib

import pytest


@pytest.fixture
def stack_land():
    return importlib.import_module("veri.stack_land")


class World:
    """What stack_branch.named answers, and every sibling script run; <answers> maps a script's name to its (exit code,
    stdout), (0, "") for one it does not name."""

    def __init__(self, monkeypatch, named, answers=None):
        self.scripts = []
        answers = answers or {}
        stack_branch = importlib.import_module("veri.stack_branch")

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

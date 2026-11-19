"""In-process cases for veri/stack_recover.py, the module stack-recover.sh is a shim over (PRD 033.3): git (git.out,
git.network), GitHub (github.gh_api), the stack branch stack-branch.sh names (stack_branch.named) and the sibling scripts
it runs (stack_fix.script) are injected in-process, so no case starts a process."""
import importlib
import json
import os
import re
import subprocess

import pytest

BASE = "1" * 40  # origin/<stack> as fetched
TIP = "9" * 40  # the local <stack>'s tip
URL = "https://github.com/owner/repo/pull/50"  # the stack's tracking pull request


@pytest.fixture
def stack_recover():
    return importlib.import_module("veri.stack_recover")


class World:
    """A repository at <tmp_path> (a main working tree, so no outage file but the one a case writes) whose stack
    branch is <named> (stack_branch.named; an exception is raised). Its refs are <refs> (a ref name to a sha), by default
    the local stack at TIP and origin's at BASE, plus origin's run branches <branches> (a name to a sha). A sha is an
    ancestor of another when the pair is in <ancestors> (by default BASE of TIP), or the two are equal. `git log` of a
    range answers <commits>, oldest first; `git show` of a commit's Veri-Joined trailer answers <trailers>' entry, else
    nothing. origin (git.network) fetches with <fetch>, an (exit code, stderr) pair, and answers every push with
    <pushes>' entry for the ref it writes (`refs/heads/<name>`, or the name a delete names), else (0, ""). GitHub reads
    each pull request of <pulls> (its number to its record), every other one as merged. The sibling scripts answer
    <answers>' entry, (exit code, stdout): merge-lock.sh (0, ""), stack-pr.sh (0, URL), any other (0, ""). Every git,
    script and GitHub call is kept, in order, in <log>: ("git", *args), (script, *args) and ("gh", path); the pushes,
    deletes among them, in <pushed>, and the scripts in <scripts>."""

    def __init__(self, monkeypatch, tmp_path, named="stack", refs=None, branches=None, ancestors=((BASE, TIP),),
                 commits=(), trailers=None, fetch=(0, ""), pushes=None, pulls=None, answers=None):
        (tmp_path / ".git").mkdir(exist_ok=True)
        monkeypatch.chdir(tmp_path)
        self.log, self.pushed, self.scripts = [], [], []
        refs = dict({"refs/heads/stack": TIP, "refs/remotes/origin/stack": BASE} if refs is None else refs)
        refs.update({"refs/remotes/origin/" + name: sha for name, sha in (branches or {}).items()})
        trailers, pushes, pulls = trailers or {}, pushes or {}, pulls or {}
        answers = dict({"stack-pr.sh": (0, URL + "\n")}, **(answers or {}))
        git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")

        def out(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:1] == ("rev-parse",):
                if args[-1] in refs:
                    return refs[args[-1]]
                raise git.GitFailed(args, 1, "")
            if args[:2] == ("merge-base", "--is-ancestor"):
                if args[2] == args[3] or (args[2], args[3]) in ancestors:
                    return ""
                raise git.GitFailed(args, 1, "")
            if args[:1] == ("log",):
                return "\n".join(commits)
            if args[:1] == ("show",):
                return trailers.get(args[-1], "")
            raise git.GitFailed(args, 128, "not faked")

        def network(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:1] == ("fetch",):
                return subprocess.CompletedProcess(["git", *args], fetch[0], "", fetch[1])
            self.pushed.append(args)
            if "--delete" in args:
                written = args[args.index("--delete") + 1]
            else:
                written = args[-1].split(":", 1)[1]
            code, said = pushes.get(written, (0, ""))
            return subprocess.CompletedProcess(["git", *args], code, "", said)

        def gh_api(path, stderr=None):
            self.log.append(("gh", path))
            number = re.fullmatch(r"repos/[^/]+/[^/]+/pulls/(\d+)", path)
            said = pulls.get(int(number[1]), {"state": "closed", "merged": True}) if number else {}
            return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(said), "")

        def answer(root):
            if isinstance(named, BaseException):
                raise named
            return named

        def script(name, *args, limit=None):
            self.log.append((name,) + args)
            self.scripts.append((name,) + args)
            return answers.get(name, (0, ""))

        monkeypatch.setattr(git, "out", out)
        monkeypatch.setattr(git, "network", network)
        monkeypatch.setattr(github, "gh_api", gh_api)
        monkeypatch.setattr(importlib.import_module("veri.stack_branch"), "named", answer)
        monkeypatch.setattr(importlib.import_module("veri.stack_fix"), "script", script)


def test_an_argument_exits_2_with_the_usage_line_and_the_shim_execs_the_module(monkeypatch, tmp_path, run_cli,
                                                                               stack_recover):
    world = World(monkeypatch, tmp_path)
    shim = os.path.join(os.path.dirname(os.path.dirname(stack_recover.__file__)), "stack-recover.sh")

    code, out, err = run_cli(stack_recover, ["--now"])

    with open(shim, encoding="utf-8") as f:
        text = f.read()
    assert (code, out, err, world.log) == (2, "", "usage: stack-recover.sh\n", []), err
    assert text.startswith("#!/bin/sh\n") and '"$(dirname "$0")/veri/stack_recover.py"' in text, text


def test_while_the_outage_file_exists_it_exits_2_in_one_stderr_line_before_any_read_or_lock(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = World(monkeypatch, tmp_path, named=AssertionError("stack-branch.sh was read"))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "github-outage").write_text("")

    code, out, err = run_cli(stack_recover, [])

    assert (code, out, err.count("\n"), world.log) == (2, "", 1, []), err
    assert "outage" in err and err.startswith("stack-recover: "), err

"""In-process cases for veri/stack_tag.py, the module stack-tag.sh is a shim over (PRD 034.4c): git (git.out,
git.network), GitHub (github.gh_api) and the merge lock (stack_fix.script) are injected in-process, so no case starts a
process."""
import importlib
import json
import re
import subprocess

import pytest

PR = "https://github.com/owner/repo/pull/90"
USAGE = "usage: stack-tag.sh <slice-pr-url> [--message <n>=<text>]...\n"


@pytest.fixture
def stack_tag():
    return importlib.import_module("veri.stack_tag")


@pytest.mark.parametrize("argv", [
    [],
    [PR, PR],
    [PR, "--message"],
    [PR, "--message", "seven=text"],
    [PR, "--message", "7"],
    ["--message", "7=text"],
])
def test_any_argument_list_but_one_url_and_message_pairs_exits_2_with_the_usage_line(run_cli, stack_tag, argv):
    code, out, err = run_cli(stack_tag, argv)

    assert (code, out, err) == (2, "", USAGE)


MERGE = "f" * 40


class World:
    """GitHub (github.gh_api) reads pull request 90 of owner/repo as <pull> (no answer when None), its commits as
    <commits>, their subjects oldest first (no answer when None), and issue <n>'s title as <titles>[n] (no answer when
    absent). git (git.out) names <default> as origin's default branch; `git log -n <k> <MERGE>` lists the landed range,
    newest first, as `<sha> <subject>` lines, its subjects <landed> (default: <commits>) and its shas `c<i>` for the
    i-th oldest; `git tag` lists <tags>, by version under `--sort=-v:refname` and lexically otherwise; `tag --points-at
    <sha>` lists <points>[sha]; `tag -a` and `tag -d` (kept in <cut>, <deleted>) add and drop a tag. origin
    (git.network) fetches, failing when <fetch_fails>, and pushes a tag, failing when it is in <push_fails>; each push is
    kept in <pushed>. merge-lock.sh (stack_fix.script) answers <lock> to take; each call is kept in <lock_calls>. Every
    call is also kept, in order, in <log>."""

    def __init__(self, monkeypatch, pull=None, commits=(), titles=None, default="main", landed=None, tags=("v0.1",),
                 points=None, push_fails=(), fetch_fails=False, lock=0):
        self.cut, self.deleted, self.pushed, self.lock_calls, self.log = [], [], [], [], []
        self.tags = list(tags)
        pull = {"merged": True, "base": {"ref": default}, "merge_commit_sha": MERGE} if pull is None else pull
        titles = titles or {}
        points = points or {}
        landed = list(commits or ()) if landed is None else landed
        git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")

        def version(tag):
            return tuple(int(part) for part in re.findall(r"\d+", tag))

        def out(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:1] == ("symbolic-ref",):
                return "origin/" + default
            if args[:1] == ("log",) and MERGE in args:
                k = int(args[args.index("-n") + 1])
                rows = [("c%d" % at, subject) for at, subject in enumerate(landed)][-k:]
                return "\n".join("%s %s" % row for row in reversed(rows))
            if args[:2] == ("tag", "--points-at"):
                return "\n".join(points.get(args[2], []) + [n for n, sha, _ in self.cut if sha == args[2]
                                                             and n not in self.deleted])
            if args[:2] == ("tag", "-a"):
                self.cut.append((args[2], args[-1], args[args.index("-m") + 1]))
                self.tags.append(args[2])
                return ""
            if args[:2] == ("tag", "-d"):
                self.deleted.append(args[2])
                self.tags.remove(args[2])
                return ""
            if args == ("tag", "--sort=-v:refname"):
                return "\n".join(sorted(self.tags, key=version, reverse=True))
            if args[:1] == ("tag",) and len(args) == 1:
                return "\n".join(sorted(self.tags))
            raise git.GitFailed(args, 128, "not faked")

        def network(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:1] == ("fetch",):
                return subprocess.CompletedProcess(["git", *args], 1 if fetch_fails else 0, "",
                                                   "fatal: unable to access origin\n" if fetch_fails else "")
            if args[:1] == ("push",):
                name = args[-1].removeprefix("refs/tags/")
                self.pushed.append(name)
                failed = name in push_fails
                return subprocess.CompletedProcess(["git", *args], 1 if failed else 0, "",
                                                   "! [rejected] %s\n" % name if failed else "")
            return subprocess.CompletedProcess(["git", *args], 128, "", "not faked\n")

        def gh_api(path, stderr=None):
            self.log.append(("gh", path))

            def said(answer):
                if answer is None:
                    return subprocess.CompletedProcess(["gh", "api", path], 1, "", "HTTP 502: Bad Gateway\n")
                return subprocess.CompletedProcess(["gh", "api", path], 0, json.dumps(answer), "")
            if path == "repos/owner/repo/pulls/90":
                return said(pull if pull != "none" else None)
            page = re.fullmatch(r"repos/owner/repo/pulls/90/commits\?per_page=100&page=(\d+)", path)
            if page:
                if commits is None:
                    return said(None)
                listed = [{"sha": "p%d" % at, "commit": {"message": subject + "\n\nbody"}}
                          for at, subject in enumerate(commits)]
                return said(listed if page[1] == "1" else [])
            issue = re.fullmatch(r"repos/owner/repo/issues/(\d+)", path)
            if issue:
                return said({"title": titles[issue[1]]} if issue[1] in titles else None)
            return said(None)

        def script(name, *args, limit=None):
            self.lock_calls.append((name,) + args)
            self.log.append((name,) + args)
            return (lock if args[:1] == ("take",) else 0), ""

        monkeypatch.setattr(git, "out", out)
        monkeypatch.setattr(git, "network", network)
        monkeypatch.setattr(github, "gh_api", gh_api)
        monkeypatch.setattr(importlib.import_module("veri.stack_fix"), "script", script)


@pytest.mark.parametrize("pull, commits, said", [
    ({"merged": False, "base": {"ref": "main"}, "merge_commit_sha": None}, ["feat: a (#7)"], "not merged"),
    ({"merged": True, "base": {"ref": "stack"}, "merge_commit_sha": MERGE}, ["feat: a (#7)"], "not main"),
    ("none", ["feat: a (#7)"], "HTTP 502"),
    (None, None, "HTTP 502"),
])
def test_a_pull_request_not_merged_into_the_default_branch_or_unread_exits_2_taking_no_lock(
        monkeypatch, run_cli, stack_tag, pull, commits, said):
    world = World(monkeypatch, pull=pull, commits=commits, titles={"7": "A capability"})

    code, out, err = run_cli(stack_tag, [PR])

    assert (code, out, said in err, world.lock_calls, world.cut) == (2, "", True, [], []), err

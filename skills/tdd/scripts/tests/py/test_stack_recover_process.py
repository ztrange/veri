"""Real-git case for veri/stack_recover.py, the module stack-recover.sh is a shim over (PRD 033.3): a clone of a local bare
origin whose local stack holds two offline joins; GitHub's pull request reads and stack-pr.sh are injected in-process,
git and merge-lock.sh run for real."""
import importlib
import json
import subprocess

import pytest

from repo_builder import git

URL = "https://github.com/owner/repo/pull/50"
PULLS = {"11": "https://github.com/owner/repo/pull/11", "12": "https://github.com/owner/repo/pull/12"}


def _commit(repo, name, message, *trailers):
    (repo / name).write_text(name + "\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message, *[arg for trailer in trailers for arg in ("--trailer", trailer)])
    return git(repo, "rev-parse", "HEAD")


def _outage_world(tmp_path):
    """A main clone (`work`) of a bare origin: origin holds trunk, the stack and the runs tdd/11-a and tdd/12-b, each run
    with its records ref; the local stack is three commits above origin's, the first and last joined offline (each a run's
    commit rebased onto the stack and amended with its Veri-Joined trailer), the middle one a stack commit of its own."""
    origin, work = tmp_path / "origin.git", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=tmp_path, check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(work)], cwd=tmp_path, check=True)
    (work / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (work / ".gitignore").write_text(".tdd/\n")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "docs: the base")
    git(work, "remote", "add", "origin", str(origin))
    git(work, "push", "-q", "origin", "trunk", "trunk:refs/heads/stack")
    for n, branch in (("11", "tdd/11-a"), ("12", "tdd/12-b")):
        git(work, "checkout", "-q", "-b", branch, "trunk")
        _commit(work, "run%s.txt" % n, "feat: run %s" % n)
        git(work, "push", "-q", "origin", "%s:refs/heads/%s" % (branch, branch), "%s:refs/veri/runs/%s" % (branch, n))
    git(work, "fetch", "-q", "origin")
    git(work, "checkout", "-q", "-b", "stack", "origin/stack")
    git(work, "checkout", "-q", "trunk")
    git(work, "worktree", "add", "-q", str(tmp_path / "joining"), "stack")
    joining = tmp_path / "joining"
    _commit(joining, "run11.txt", "feat: run 11", "Veri-Joined: %s tdd/11-a" % PULLS["11"])
    _commit(joining, "own.txt", "fix: a stack commit of its own")
    tip = _commit(joining, "run12.txt", "feat: run 12", "Veri-Joined: %s tdd/12-b" % PULLS["12"])
    git(work, "worktree", "remove", str(joining))
    return origin, work, tip


@pytest.mark.process("git against a local bare origin, and merge-lock.sh run as its /bin/sh shim, from stack-recover's"
                     " module run in-process")
def test_recovers_two_offline_joins_end_to_end_pushing_each_branch_and_the_stack_and_deleting_each_runs_refs(
        tmp_path, monkeypatch, run_cli):
    origin, work, tip = _outage_world(tmp_path)
    github, stack_fix = importlib.import_module("veri.github"), importlib.import_module("veri.stack_fix")
    monkeypatch.setattr(github, "gh_api", lambda path, stderr=None: subprocess.CompletedProcess(
        ["gh", "api", path], 0, json.dumps({"state": "closed", "merged": True}), ""))
    real = stack_fix.script
    monkeypatch.setattr(stack_fix, "script", lambda name, *args, **kwargs: (
        (0, URL + "\n") if name == "stack-pr.sh" else real(name, *args, **kwargs)))
    recover = importlib.import_module("veri.stack_recover")

    code, out, err = run_cli(recover, [], cwd=work)

    refs = git(origin, "for-each-ref", "--format=%(refname) %(objectname)").splitlines()
    assert (code, out) == (0, "%s %s\n" % (tip, URL)), err
    assert sorted(refs) == sorted(["refs/heads/stack " + tip, "refs/heads/trunk " + git(work, "rev-parse", "trunk")]), err

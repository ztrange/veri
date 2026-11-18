"""Process cases for stack-carry.sh, the shim over veri/stack_carry.py (PRD 034.4b, KL28): the carry-over measurement's
four scenarios with real git. A bare origin whose default branch is `trunk` holds a 10-commit stack cut at its 6th
commit; the slice lands on trunk as GitHub's rebase-merge would (each commit re-created by another committer), after
trunk was untouched, moved by an unrelated file, moved by an edit near a slice commit, or moved by an edit that conflicts
with a later stack commit. A stub gh answers stack-pr.sh with one open tracking pull request."""
import json
import os
import subprocess

import pytest

from repo_builder import git
from stub_script import write_stub

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-carry.sh"))
GH = """here="$(dirname "$0")"
case "$*" in
  *"pulls?state=open"*) cat "$here/list.out" ;;
  *) exit 1 ;;
esac
"""
TRACKING = {"number": 1, "html_url": "https://github.com/o/r/pull/1", "draft": False, "state": "open",
            "head": {"ref": "stack", "sha": "abc", "label": "o:stack", "repo": {"full_name": "o/r"}},
            "base": {"ref": "trunk", "repo": {"full_name": "o/r"}}}
SHARED = "".join("line %d\n" % n for n in range(1, 21))
# How trunk moves before the slice lands: a file and its text, or None for untouched.
MOVES = {
    "base": None,
    "mx_ok": ("unrelated.txt", "another team's file\n"),
    "mx_ctx": ("shared.txt", SHARED.replace("line 8\n", "line 8 edited on trunk\n")),
    "mx_conflict": ("f8.txt", "trunk's own line\n"),
}
RUN_CUTS = (3, 6, 8)


def commit(repo, path, text, subject):
    (repo / path).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", subject)
    return git(repo, "rev-parse", "HEAD")


def world(tmp_path, move):
    """A main clone (`work`) of a bare origin, the stack's ten commits, and trunk with the slice (the first six) landed
    after <move>: (work, author clone, the stack's shas)."""
    origin, author, work = tmp_path / "origin.git", tmp_path / "author", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(author)], cwd=str(tmp_path), check=True)
    (author / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (author / ".gitignore").write_text(".tdd/\n")
    (author / "f8.txt").write_text("the original line\n")
    commit(author, "shared.txt", SHARED, "docs: the base (#1)")
    git(author, "remote", "add", "origin", str(origin))
    git(author, "push", "-q", "origin", "trunk")
    git(author, "checkout", "-q", "-b", "stack")
    stack = []
    for n in range(1, 11):
        if n == 3:
            stack.append(commit(author, "shared.txt", SHARED.replace("line 5\n", "line 5 edited by the stack\n"),
                                "feat: three (#%d)" % (100 + n)))
        elif n == 8:
            stack.append(commit(author, "f8.txt", "the stack's own line\n", "feat: eight (#%d)" % (100 + n)))
        else:
            stack.append(commit(author, "s%d.txt" % n, "stack %d\n" % n, "feat: s%d (#%d)" % (n, 100 + n)))
    git(author, "push", "-q", "origin", "stack")
    for cut in RUN_CUTS:
        git(author, "checkout", "-q", "-b", "tdd/%d-run" % cut, stack[cut - 1])
        for k in (1, 2):
            commit(author, "run%d-%d.txt" % (cut, k), "run\n", "feat: run %d own %d (#%d)" % (cut, k, 200 + cut))
        git(author, "push", "-q", "origin", "tdd/%d-run" % cut)
    git(author, "checkout", "-q", "trunk")
    if MOVES[move]:
        commit(author, *MOVES[move], "feat: trunk moved (#50)")
    git(author, "-c", "user.name=lander", "-c", "user.email=lander@example.test", "cherry-pick", "--allow-empty",
        "%s..%s" % (stack[0] + "~1", stack[5]))
    git(author, "push", "-q", "origin", "trunk")
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], cwd=str(tmp_path), check=True)
    return work, author, stack


def gh_on_path(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "list.out").write_text(json.dumps([TRACKING]))
    return {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}


def remote(work, ref):
    return git(work, "ls-remote", "origin", ref).split()[0]


@pytest.mark.process("stack-carry.sh run as its /bin/sh shim in a real clone of a local bare origin, with a stub gh on"
                     " PATH, force-pushing the stack under a lease to that origin")
@pytest.mark.timeout(120)
@pytest.mark.parametrize("move", ["base", "mx_ok", "mx_ctx"])
def test_the_measured_scenarios_carry_the_stack_to_a_tip_the_merge_tree_check_equals_and_each_run_rebases_onto_it_with_only_its_own_commits(
        tmp_path, move):
    work, author, stack = world(tmp_path, move)
    runs = {cut: remote(work, "refs/heads/tdd/%d-run" % cut) for cut in RUN_CUTS}
    head = git(work, "rev-parse", "HEAD")

    done = subprocess.run([SHIM, stack[5]], cwd=str(work), env=gh_on_path(tmp_path), capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=90)

    git(work, "fetch", "-q", "origin")
    new = git(work, "rev-parse", "origin/stack")
    checked = git(work, "merge-tree", "--write-tree", "--merge-base=" + stack[5], "origin/trunk", stack[9])
    assert (done.returncode, done.stdout.split(), checked.splitlines()[0], git(work, "rev-parse", new + "^{tree}"),
            git(work, "merge-base", "--is-ancestor", "origin/trunk", new) == "") == (
        0, [new], git(work, "rev-parse", new + "^{tree}"), checked.splitlines()[0], True), done.stderr
    assert {cut: remote(work, "refs/heads/tdd/%d-run" % cut) for cut in RUN_CUTS} == runs
    left = os.listdir(work / ".tdd") if (work / ".tdd").exists() else []
    assert (git(work, "status", "--porcelain"), git(work, "rev-parse", "HEAD"), left,
            git(work, "worktree", "list", "--porcelain").count("worktree ")) == ("", head, [], 1)
    for cut in RUN_CUTS:
        git(work, "checkout", "-q", "-b", "check-%d" % cut, "origin/tdd/%d-run" % cut)
        git(work, "rebase", "-q", "--onto", "origin/stack", stack[cut - 1])
        own = git(work, "log", "--format=%s", "origin/stack..HEAD").splitlines()
        assert own == ["feat: run %d own 2 (#%d)" % (cut, 200 + cut), "feat: run %d own 1 (#%d)" % (cut, 200 + cut)]
        git(work, "checkout", "-q", "trunk")


@pytest.mark.process("stack-carry.sh run as its /bin/sh shim in a real clone of a local bare origin whose trunk moved by"
                     " an edit that conflicts with a later stack commit")
@pytest.mark.timeout(120)
def test_a_trunk_edit_conflicting_with_a_later_stack_commit_exits_1_naming_the_file_with_origin_stack_unchanged(tmp_path):
    work, author, stack = world(tmp_path, "mx_conflict")

    done = subprocess.run([SHIM, stack[5]], cwd=str(work), env=gh_on_path(tmp_path), capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=90)

    leftovers = os.listdir(work / ".tdd") if (work / ".tdd").exists() else []
    assert (done.returncode, "f8.txt" in done.stderr, remote(work, "refs/heads/stack"), leftovers,
            git(work, "worktree", "list", "--porcelain").count("worktree ")) == (1, True, stack[9], [], 1), done.stderr


@pytest.mark.process("stack-carry.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_the_shim_with_no_argument_exits_2_with_its_usage_line(tmp_path):
    ran = subprocess.run([SHIM], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: stack-carry.sh <old-cut>\n")

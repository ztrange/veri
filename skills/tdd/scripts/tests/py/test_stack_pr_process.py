"""Process cases for stack-pr.sh, the shim over veri/stack_pr.py: a real git clone of a local bare origin whose default
branch is `trunk`, with a stack branch, and a stub gh answering from files the case writes."""
import json
import os
import subprocess

import pytest

from repo_builder import git
from stub_script import write_stub

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-pr.sh"))
GH = """log="$(dirname "$0")/gh.log"
printf '%s\\n' "$*" >> "$log"
here="$(dirname "$0")"
case "$*" in
  *"-X POST"*) cat "$here/create.out"; exit "$(cat "$here/create.rc")" ;;
  *"pulls?state=open"*) cat "$here/list.out"; exit "$(cat "$here/list.rc")" ;;
esac
exit 1
"""


def pull(number, draft=False):
    return {"number": number, "html_url": "https://github.com/o/r/pull/%d" % number, "draft": draft,
            "head": {"ref": "stack", "sha": "abc", "label": "o:stack", "repo": {"full_name": "o/r"}},
            "base": {"ref": "trunk", "repo": {"full_name": "o/r"}}, "state": "open"}


def clone_with_stack(tmp_path, ahead=True):
    """A clone of a bare origin whose default branch is trunk, its CLAUDE.md naming the stack branch `stack`, which
    origin holds <ahead> of trunk by two commits, else at trunk's tip."""
    origin, seed, work = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(seed)], cwd=str(tmp_path), check=True)
    (seed / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    git(seed, "add", "CLAUDE.md")
    git(seed, "commit", "-q", "-m", "docs: name the stack (#1)")
    git(seed, "remote", "add", "origin", str(origin))
    git(seed, "push", "-q", "origin", "trunk")
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], cwd=str(tmp_path), check=True)
    git(work, "checkout", "-q", "-b", "stack")
    for n, subject in enumerate(("feat: one (#2)", "fix: two (#3)")[:2 if ahead else 0]):
        (work / ("f%d" % n)).write_text(subject)
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", subject)
    git(work, "push", "-q", "origin", "stack")
    return work


def gh_answering(tmp_path, listed=(), list_rc=0, created=None, create_rc=0):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "list.out").write_text(json.dumps(list(listed)))
    (bin_dir / "list.rc").write_text(str(list_rc))
    (bin_dir / "create.out").write_text(json.dumps(created) if created is not None else "")
    (bin_dir / "create.rc").write_text(str(create_rc))
    return bin_dir


def run_shim(work, bin_dir):
    env = {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}
    done = subprocess.run([SHIM], cwd=str(work), env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          timeout=60)
    log = bin_dir / "gh.log"
    calls = log.read_text().splitlines() if log.exists() else []
    return done.returncode, done.stdout, done.stderr, [c for c in calls if "-X POST" in c]


@pytest.mark.process("stack-pr.sh run as its /bin/sh shim in a clone of a local bare origin (default branch trunk), with a stub gh on PATH")
@pytest.mark.parametrize("gh, expected", [
    (dict(listed=[pull(4)]), (0, "https://github.com/o/r/pull/4\n", False, 0)),
    (dict(created=pull(9)), (0, "https://github.com/o/r/pull/9\n", False, 1)),
    (dict(listed=[pull(4), pull(5)]), (2, "", True, 0)),
    (dict(listed=[pull(4, draft=True)]), (2, "", True, 0)),
    (dict(create_rc=1), (2, "", True, 1)),
    (dict(list_rc=1), (2, "", True, 0)),
])
def test_stack_pr_prints_the_one_tracking_pull_request_opening_it_only_when_none_is_open_and_exits_2_without_an_answer(
        tmp_path, gh, expected):
    work = clone_with_stack(tmp_path)

    code, out, err, posts = run_shim(work, gh_answering(tmp_path, **gh))

    assert (code, out, err.startswith("stack-pr: "), len(posts)) == expected, err


@pytest.mark.process("stack-pr.sh run as its /bin/sh shim in a clone of a local bare origin whose stack is at trunk's tip, with a stub gh on PATH")
def test_stack_pr_with_the_stack_not_ahead_exits_3_reading_and_opening_nothing(tmp_path):
    work = clone_with_stack(tmp_path, ahead=False)
    bin_dir = gh_answering(tmp_path)

    code, out, err, posts = run_shim(work, bin_dir)

    assert (code, out, posts, (bin_dir / "gh.log").exists()) == (3, "", [], False), err

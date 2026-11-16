"""A run's local records carried on origin's `refs/veri/runs/<n>`: a commit on no branch holding the issue's lines of
`.tdd/events.jsonl`, its `.tdd/issue-<n>-skill-commit` and its `.tdd/issue-<n>-timeout`, so another machine's
metrics and resume read them. Never committed on the run's branch: rebase-merge would carry them into main's history."""
import json
import os
import sys

import git
import run_dir

IDENTITY = {"GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@localhost",
            "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@localhost"}
EVENTS = ".tdd/events.jsonl"


def ref(issue):
    return "refs/veri/runs/%s" % issue


def _issue_lines(path, issue):
    try:
        with open(path, "rb") as f:
            raw = f.read().splitlines(keepends=True)
    except OSError:
        return b""
    kept = []
    for line in raw:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict) and str(record.get("issue", "")) == str(issue):
            kept.append(line if line.endswith(b"\n") else line + b"\n")
    return b"".join(kept)


def _first_file(roots, issue, suffix):
    for root in roots:
        try:
            with open(run_dir.issue_file(root, issue, suffix), "rb") as f:
                return f.read()
        except OSError:
            continue
    return None


def records(run, issue):
    """{name under .tdd/: bytes} for the run at <run>: its journal lines for <issue>, and the skill pin and timeout pin,
    each read from the run, else from the main tree it sits under; a file the run lacks is left out."""
    roots = [run] + [m for m in [run_dir.main_of_worktree(os.path.abspath(run))] if m]
    found = {}
    lines = _issue_lines(os.path.join(run, EVENTS), issue)
    if lines:
        found["events.jsonl"] = lines
    for suffix in ("-skill-commit", "-timeout"):
        content = _first_file(roots, issue, suffix)
        if content is not None:
            found["issue-%s%s" % (issue, suffix)] = content
    return found


def _out(*args, cwd, data=None, env=None):
    done = git.git(*args, cwd=cwd, input=data, capture_output=True,
                   env=None if env is None else {**os.environ, **env})
    if done.returncode != 0:
        raise git.GitFailed(args, done.returncode, os.fsdecode(done.stderr))
    return os.fsdecode(done.stdout).strip()


def commit(run, issue):
    """The commit (no parent, on no branch) holding <run>'s records for <issue> under `.tdd/`; GitFailed on a git error."""
    entries = []
    for name, content in sorted(records(run, issue).items()):
        blob = _out("hash-object", "-w", "--stdin", cwd=run, data=content)
        entries.append("100644 blob %s\t%s\n" % (blob, name))
    inner = _out("mktree", cwd=run, data="".join(entries).encode())
    outer = _out("mktree", cwd=run, data=("040000 tree %s\t.tdd\n" % inner).encode())
    return _out("commit-tree", outer, "-m", "veri: run records of #%s" % issue, cwd=run, env=IDENTITY)


def push(run, issue):
    """Replace origin's `refs/veri/runs/<issue>` with the commit of <run>'s records; GitFailed on a git error."""
    _out("push", "-q", "--force", "origin", "%s:%s" % (commit(run, issue), ref(issue)), cwd=run)


def read(issue, name, cwd):
    """The text of `.tdd/<name>` in origin's `refs/veri/runs/<issue>`, fetched into the clone at <cwd> under the same
    ref; None when origin has no such ref or file, or cannot be reached."""
    if git.git("fetch", "-q", "origin", "+%s:%s" % (ref(issue), ref(issue)), cwd=cwd, capture_output=True).returncode:
        return None
    shown = git.git("show", "%s:.tdd/%s" % (ref(issue), name), cwd=cwd, capture_output=True)
    return os.fsdecode(shown.stdout) if shown.returncode == 0 else None


def delete(issue, cwd):
    """Delete origin's `refs/veri/runs/<issue>`, from the clone at <cwd>; one origin never had is already gone.
    GitFailed on any other git error."""
    done = git.git("push", "origin", "--delete", ref(issue), cwd=cwd, capture_output=True, text=True)
    if done.returncode != 0 and "remote ref does not exist" not in done.stderr:
        raise git.GitFailed(("push", "origin", "--delete", ref(issue)), done.returncode, done.stderr)


def after_push():
    """push, for the issue the current branch `tdd/<n>-<slug>` names, from the working directory; nothing on another
    branch. A git failure is one stderr line and never an exit code: the records mirror the run."""
    issue = None
    try:
        issue = run_dir.branch_issue(git.out("rev-parse", "--abbrev-ref", "HEAD"))
        if issue:
            push(".", issue)
    except git.GitFailed as failed:
        print("push-branch.sh: %s not pushed: %s" % (ref(issue or "<n>"), " ".join((failed.stderr or str(failed)).split())),
              file=sys.stderr)

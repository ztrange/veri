"""github-queue.sh: the issue writes a live run makes while GitHub is down, queued and replayed in order, run in-process.

The queue is `.tdd/github-queue` in the repository's main working tree (found from any worktree through git's common
directory), one JSON object per line, in the order the writes were made: a `comment` entry (`issue`, `kind`, `body`,
`key`), its body already redacted and ending in the hidden marker `<!-- veri-queued <key> -->`, or a `tick` entry
(`issue`, `criterion`, `key`), the issue's acceptance criterion `<criterion>` to tick. GitHub is down while
`.tdd/github-outage` exists in the main working tree or `github-status.sh`'s read with its default components reports
a counting incident; a read that gets no answer is not an outage. Every append and every replay holds an exclusive
lock on `.tdd/github-queue.lock`, a file never removed; the queue is rewritten by renaming a temporary file."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import fcntl
import json
import os
import secrets
import sys

import entry
import github
import github_outage
import github_status
import issue_body
import ledger
import run_dir
import tick_issue_criterion

USAGE = "usage: github-queue.sh replay"
FILE, LOCK = ".tdd/github-queue", ".tdd/github-queue.lock"
MARKER = "<!-- veri-queued %s -->"


def root(start=None):
    """The main working tree the queue lives in, found from <start> (default: the current directory); None when a
    linked worktree's gitdir cannot be read, so nothing is queued or replayed there."""
    try:
        return run_dir.main_tree_from_files(start)
    except OSError:
        return None


def incident():
    """Whether github-status.sh's read with its default components reports a counting incident; no answer is not one."""
    try:
        return github_outage.status_read()[0] == 1
    except github_status.NoAnswer:
        return False


def outage(top):
    """Whether the dev session's local mode is on: `.tdd/github-outage` exists in the main working tree <top>."""
    return os.path.exists(os.path.join(top, github_outage.FILE))


def down(top):
    """GitHub is down: the outage file exists, or the status read reports an incident (read only without the file)."""
    return outage(top) or incident()


@contextlib.contextmanager
def locked(top):
    os.makedirs(os.path.join(top, ".tdd"), exist_ok=True)
    with open(os.path.join(top, LOCK), "a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def lines_of(top):
    """The queue's lines, or None when there is no queue."""
    try:
        with open(os.path.join(top, FILE), encoding="utf-8") as handle:
            return handle.read().splitlines()
    except FileNotFoundError:
        return None


def pending(top):
    """Whether the queue holds an entry."""
    return top is not None and bool(lines_of(top))


def append(top, entry_):
    """Add <entry_> as the queue's last line, under the lock."""
    with locked(top):
        with open(os.path.join(top, FILE), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry_, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def key():
    return secrets.token_hex(8)


def queue_comment(top, issue, kind, body):
    """Queue a comment of <kind> on <issue>, <body> redacted and ending in its key's marker; the key."""
    k = key()
    append(top, {"type": "comment", "issue": str(issue), "kind": kind,
                 "body": "%s\n\n%s" % (github.published(body).rstrip("\n"), MARKER % k), "key": k})
    return k


def queue_tick(top, issue, criterion):
    """Queue the tick of <issue>'s acceptance criterion <criterion>; the key."""
    k = key()
    append(top, {"type": "tick", "issue": str(issue), "criterion": int(criterion), "key": k})
    return k

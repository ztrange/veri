#!/usr/bin/env python3
"""push_branch — copy the run's branch to the remote, from the worktree it runs in.

Port of push-branch.sh (measurement spike). The CLI contract is the bash script's, byte
for byte: no arguments; VERI_PUSH_RETRIES (default 3) extra attempts after the first and
VERI_PUSH_BACKOFF (default 2) seconds between them, doubled per wait; an unreachable
remote exits 0 after one stderr line and one `push-failed` event; a non-fast-forward
rejection exits 1 after one attempt, naming the remote sha, with a `push-rejected` event;
a bad tunable exits 2 before any push; an event that cannot be written exits 2.

The event is recorded by the sibling `event.sh`, found beside the entry script, and the
wait is the `sleep` binary rather than time.sleep: the integration suite observes both
through PATH, so they stay processes. A unit test replaces `run`, `sleep_for` and
`record` in-process instead.
"""
import os
import re
import subprocess
import sys

_INTEGER = re.compile(r"[0-9]+")


def _decode(b):
    return b.decode("utf-8", "surrogateescape")


def run(argv):
    """Run a command the way `$(cmd 2>&1)` does: (returncode, combined output with its
    trailing newlines stripped). A missing binary reads as a failed command, the way bash's
    `command not found` (127) does."""
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as e:
        return 127, "push-branch.sh: %s: %s" % (argv[0], e.strerror)
    return p.returncode, _decode(p.stdout).rstrip("\n")


def run_stdout(argv):
    """`$(cmd)`: stdout only, trailing newlines stripped, stderr left where it is."""
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE)
    except OSError:
        return ""
    return _decode(p.stdout).rstrip("\n")


def sleep_for(seconds):
    """`sleep "$backoff"` as a process, so a stub `sleep` on PATH sees it."""
    try:
        subprocess.run(["sleep", str(seconds)])
    except OSError:
        pass


def script_dir():
    """The scripts/ directory this module's py/ sits under — where the bash script's
    `dirname "$0"` found event.sh. abspath, not realpath: a skill reached through the
    ~/.claude/skills symlink keeps its logical path the way `cd … && pwd` did."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def record(event, *pairs):
    """Append an event through event.sh, or exit 2 if it cannot be written."""
    try:
        p = subprocess.run([os.path.join(script_dir(), "event.sh"), event, *pairs])
        rc = p.returncode
    except OSError:
        rc = 127
    if rc != 0:
        sys.exit(2)


def read_tunables(environ, stderr):
    """Return (retries, backoff) as ints, or None after the bash script's exit-2 line."""
    values = [
        ("VERI_PUSH_RETRIES", environ.get("VERI_PUSH_RETRIES") or "3"),
        ("VERI_PUSH_BACKOFF", environ.get("VERI_PUSH_BACKOFF") or "2"),
    ]
    for name, value in values:
        if not _INTEGER.fullmatch(value):
            stderr.write("push-branch.sh: %s must be a non-negative integer, got '%s'\n" % (name, value))
            stderr.flush()
            return None
    return int(values[0][1]), int(values[1][1])


def is_rejection(out):
    return "[rejected]" in out and (
        "non-fast-forward" in out or "fetch first" in out or "stale info" in out
    )


def main(environ=None, stderr=None):
    environ = os.environ if environ is None else environ
    stderr = sys.stderr if stderr is None else stderr
    tunables = read_tunables(environ, stderr)
    if tunables is None:
        return 2
    retries, backoff = tunables
    attempt = 0
    out = ""
    while attempt <= retries:
        attempt += 1
        rc, out = run(["git", "push", "--set-upstream", "origin", "HEAD"])
        if rc == 0:
            return 0
        if is_rejection(out):
            branch = run_stdout(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            ls = run_stdout(["git", "ls-remote", "origin", "refs/heads/" + branch])
            remote_sha = "\n".join(line.split("\t", 1)[0] for line in ls.split("\n")).rstrip("\n")
            stderr.write("push rejected (non-fast-forward): origin/%s is at %s\n" % (branch, remote_sha))
            stderr.flush()
            record("push-rejected", "remote_sha=" + remote_sha, "error=" + out)
            return 1
        if attempt <= retries:
            sleep_for(backoff)
            backoff *= 2
    stderr.write("push-branch.sh: push failed after %d attempts; the branch is not on the remote\n" % attempt)
    stderr.flush()
    record("push-failed", "error=" + out, "attempts=%d" % attempt)
    return 0


if __name__ == "__main__":
    sys.exit(main())

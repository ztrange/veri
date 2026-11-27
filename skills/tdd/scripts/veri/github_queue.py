"""github-queue.sh: the issue writes a live run makes while GitHub is down, queued and replayed in order,
run in-process.

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
import github_status
import issue_body
import ledger
import run_dir
import tick_issue_criterion

USAGE = "usage: github-queue.sh replay"
FILE, LOCK = ".tdd/github-queue", ".tdd/github-queue.lock"
OUTAGE_FILE = ".tdd/github-outage"  # github_outage.FILE; a Conductors module no GitHub one imports
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
        return github_status.default_read()[0] == 1
    except github_status.NoAnswer:
        return False


def outage(top):
    """Whether the dev session's local mode is on: `.tdd/github-outage` exists in the main working tree <top>."""
    return os.path.exists(os.path.join(top, OUTAGE_FILE))


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
    """The queue's lines, split on newlines only, so a body's U+2028, U+2029 or U+0085 stays inside its entry; None
    when there is no queue."""
    try:
        with open(os.path.join(top, FILE), encoding="utf-8", newline="") as handle:
            return handle.read().split("\n")
    except FileNotFoundError:
        return None


def entries_of(top):
    """The queue's non-blank lines; none when there is no queue."""
    return [line for line in lines_of(top) or [] if line.strip()]


def pending(top):
    """Whether the queue holds an entry."""
    return top is not None and bool(entries_of(top))


def append(top, entry_):
    """Add <entry_> as the queue's last line, under the lock."""
    with locked(top):
        with open(os.path.join(top, FILE), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry_) + "\n")
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


def rewrite(top, lines):
    """Replace the queue with <lines> by renaming a temporary file; no lines removes it."""
    path = os.path.join(top, FILE)
    if not lines:
        os.remove(path)
        return
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write("".join(line + "\n" for line in lines))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def criterion_line(body, k):
    """The line of acceptance criterion <k> in issue body <body>, as `ledger-steps.sh criterion <k>` prints it; None
    when the body has no such criterion."""
    found = issue_body.criteria(body, prefix=True, occurrence="all")
    records = ledger.ledger_steps("\n".join(line for _, line in found))
    return records[k - 1].text if 1 <= k <= len(records) else None


def parsed(line):
    """Queue line <line> as its entry; ValueError when it is not one."""
    try:
        e = json.loads(line)
        kind = e.get("type")
    except (ValueError, AttributeError) as error:
        raise ValueError(str(error)) from None
    if kind not in ("comment", "tick"):
        raise ValueError("type %r" % kind)
    return e


def blocked(top):
    """Whether the queue's first entry is unreadable, so a replay can never get past it."""
    lines = entries_of(top)
    try:
        lines and parsed(lines[0])
    except ValueError:
        return True
    return False


def land(e):
    """Make queued entry <e>'s write; NoAnswer when GitHub gives none."""
    if e["type"] == "comment":
        marker = MARKER % e["key"]
        comments = github.issue_comments(e["issue"])
        if any(github.trusted_comment(c) and marker in (c.get("body") or "") for c in comments):
            return
        github.gh_issue_comment(e["issue"], github.published(e["body"]))
        return
    line = criterion_line(github.gh_issue_view(e["issue"], "body"), int(e["criterion"]))
    if line is None:
        print("github-queue.sh: dropped tick %s: #%s has no criterion %s any more"
              % (e["key"], e["issue"], e["criterion"]), file=sys.stderr)
    elif tick_issue_criterion.tick(e["issue"], line) == 2:
        raise github.NoAnswer("")


def replay(top, out=None):
    """Post the queue's entries in file order, removing each that landed (exit 0 once empty, 3 with no queue); stop at
    the first that gets no answer, naming it, keeping it and every later one (exit 2)."""
    with locked(top):
        lines = lines_of(top)
        if lines is None:
            return 3
        lines = [line for line in lines if line.strip()]
        while lines:
            try:
                e = parsed(lines[0])
            except ValueError as error:
                return entry.refuse("github-queue.sh: unreadable entry in %s: %s" % (FILE, error))
            try:
                land(e)
            except github.NoAnswer:
                return entry.refuse("github-queue.sh: no answer replaying %s (%s on #%s); it and the %d after it stay "
                                    "queued" % (e.get("key"), e["type"], e.get("issue"), len(lines) - 1))
            lines = lines[1:]
            rewrite(top, lines)
            print("replayed %s" % e.get("key"), file=out or sys.stdout)
        if os.path.exists(os.path.join(top, FILE)):
            rewrite(top, [])
        return 0


def main(argv):
    if argv != ["replay"]:
        return entry.refuse(usage=USAGE)
    top = root()
    if top is None:
        return entry.refuse("github-queue.sh: no main working tree")
    return replay(top)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])

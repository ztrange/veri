"""github-queue.sh: the issue writes a live run makes while GitHub is down, queued and replayed in order,
run in-process.

The queue is `.tdd/github-queue` in the repository's main working tree (found from any worktree through git's common
directory), one JSON object per line, in the order the writes were made: a `comment` entry (`issue`, `kind`, `body`,
`key`), its body already redacted and ending in the hidden marker `<!-- veri-queued <key> -->`, or a `tick` entry
(`issue`, `criterion`, `key`), the issue's acceptance criterion `<criterion>` to tick. GitHub is down while
`.tdd/github-outage` exists in the main working tree or `github-status.sh`'s read with its default components reports
a counting incident; a read that gets no answer is not an outage. Every append and every replay holds an exclusive
lock on `.tdd/github-queue.lock`, a file never removed; the queue is rewritten by renaming a temporary file.

`close-landed <tip-sha>` queues, then replays, one `### ✅ Landed` comment per issue an offline join landed: it fetches
origin, reads `<tip-sha>..origin/<default>`, the commits the stack landed as, and credits each run, the commit carrying
a `Veri-Joined: <pr-url> <branch>` trailer, only the landed copies of `<onto>..<join>`, `<onto>` being its
`Veri-Joined-Onto: <sha>` trailer, so a subject needs no `(#<n>)` suffix and an online join, a repair or a held pull
request is credited to no run. A run whose join has not landed gets no comment, and a join without one full-sha
`Veri-Joined-Onto` exits 2. Only a run whose pull request reads as merged gets its comment; the comment's key is
derived from the issue and the landed commits, not the tip, so a second run over the same landed commits posts
nothing, whatever tip it is given, and a later landing of more of an issue's commits posts it a second comment."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import fcntl
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys

import entry
import git
import github
import github_status
import issue_body
import ledger
import run_dir
import tick_issue_criterion

USAGE = "usage: github-queue.sh replay | close-landed <tip-sha>"
FILE, LOCK = ".tdd/github-queue", ".tdd/github-queue.lock"
OUTAGE_FILE = ".tdd/github-outage"  # github_outage.FILE; a Conductors module no GitHub one imports
MARKER = "<!-- veri-queued %s -->"
SHA = re.compile(r"[0-9a-f]{7,40}")
JOINED = re.compile(r"https://[^/\s]+/([^/\s]+/[^/\s]+)/pull/(\d+) (\S+)")


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


def queue_comment(top, issue, kind, body, k=None):
    """Queue a comment of <kind> on <issue>, <body> redacted and ending in the marker of key <k> (default: a random
    one); the key."""
    k = k or key()
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


AUTHORED = "%an%x1f%ae%x1f%at%x1f%B"


def _authored(*revs):
    """[(author, email, author time, message, sha, short sha, subject)] of the commits <revs> name, oldest first: the
    first four are what a rebase or a cherry-pick keeps, so they find a commit's landed copy."""
    log = git.out("log", "--reverse", "--format=%x1e" + AUTHORED + "%x1f%H%x1f%h%x1f%s", *revs, "--")
    return [tuple(record.rstrip("\n").split("\x1f")) for record in log.split("\x1e")[1:]]


def _trailer(key):
    return "%%(trailers:key=%s,valueonly,unfold,separator=%%x1d)" % key


def joined_runs(tip, default):
    """The offline joins `<tip>..origin/<default>` landed, oldest first: (issue, pull request url, api path,
    [(sha, short sha, subject)]) each. A run is a commit of <tip>'s history outside origin's carrying a Veri-Joined
    trailer, and its commits are only those its own join added: the landed copies of `<onto>..<that commit>`, <onto>
    being its Veri-Joined-Onto trailer, the stack's tip the join was made onto. So a run joined online before the
    outage, a repair committed between two joins and a held pull request merged first are no run's. A run whose
    Veri-Joined commit did not land is left out. ValueError naming the commit when its Veri-Joined or Veri-Joined-Onto
    trailer cannot be read as one run's."""
    landed = {record[:4]: record[4:] for record in _authored("%s..refs/remotes/origin/%s" % (tip, default))}
    log = git.out("log", "--reverse", "--format=%x1e%H%x1f%h%x1f%s%x1f" + _trailer("Veri-Joined") + "%x1f"
                  + _trailer("Veri-Joined-Onto"), tip, "^refs/remotes/origin/%s" % default, "--")
    runs = []
    for record in log.split("\x1e")[1:]:
        sha, short, subject, trailers, ontos = record.rstrip("\n").split("\x1f")
        values = [value for value in trailers.split("\x1d") if value]
        if not values:
            continue
        found = JOINED.fullmatch(values[0].strip())
        issue = found and run_dir.branch_issue(found[3])
        if len(values) > 1 or not issue:
            raise ValueError("%s %s: Veri-Joined %r is not one `<pr-url> tdd/<n>-<slug>`" % (short, subject, trailers))
        bases = [value.strip() for value in ontos.split("\x1d") if value.strip()]
        if len(bases) != 1 or not re.fullmatch(r"[0-9a-f]{40}", bases[0]):
            raise ValueError("%s %s: Veri-Joined-Onto %r is not the one commit sha the join was made onto"
                             % (short, subject, ontos))
        try:
            own = _authored("%s..%s" % (bases[0], sha))
        except git.GitFailed as error:
            raise ValueError("%s %s: cannot read %s..%s from its Veri-Joined-Onto trailer (%s)"
                             % (short, subject, bases[0][:12], short, (error.stderr or "").strip())) from error
        if own and own[-1][:4] in landed:
            commits = [landed[record[:4]] for record in own if record[:4] in landed]
            runs.append((issue, found[0].split(" ")[0], "repos/%s/pulls/%s" % (found[1], found[2]), commits))
    return runs


def merged(path):
    """Whether the pull request at api <path> reads as merged; None when the read gets no answer."""
    try:
        done = github.gh_api(path, stderr=subprocess.PIPE)
        return json.loads(done.stdout).get("merged") is True if done.returncode == 0 else None
    except (github.NoAnswer, ValueError, AttributeError):
        return None


def close_landed(top, tip):
    """Queue and replay one `### ✅ Landed` comment per issue whose offline join landed between stack tip <tip> and
    origin's default branch, listing its commits there; exit 2 when origin, the range or a pull request gets no
    answer or a Veri-Joined trailer is garbled, else the replay's code (3: nothing queued)."""
    fetched = git.network("fetch", "origin", cwd=top)
    if fetched.returncode != 0:
        return entry.refuse("github-queue.sh: git fetch origin failed; no Landed comment queued",
                            fetched.stderr.strip())
    default = git.default_branch(top)
    if not default:
        return entry.refuse("github-queue.sh: cannot tell origin's default branch; no Landed comment queued")
    try:
        runs = joined_runs(tip, default)
    except git.GitFailed as error:
        return entry.refuse("github-queue.sh: cannot read %s..origin/%s; no Landed comment queued" % (tip, default),
                            (error.stderr or "").strip())
    except ValueError as error:
        return entry.refuse("github-queue.sh: %s; no Landed comment queued" % error)
    if not runs:
        print("github-queue.sh: no Veri-Joined commit in %s..origin/%s" % (tip, default), file=sys.stderr)
        return 3
    landed, failed = {}, False
    for issue, url, path, commits in runs:
        answer = merged(path)
        if answer is None:
            failed = True
            print("github-queue.sh: no answer reading #%s's pull request %s; no Landed comment for it"
                  % (issue, url), file=sys.stderr)
        elif not answer:
            print("github-queue.sh: #%s's pull request %s is not merged; no Landed comment for it" % (issue, url),
                  file=sys.stderr)
        else:
            landed.setdefault(issue, []).extend(commits)
    for issue, commits in landed.items():
        shas = " ".join(sha for sha, _, _ in commits)
        k = hashlib.sha256(("%s %s" % (issue, shas)).encode()).hexdigest()[:16]
        body = "### ✅ Landed\n\n%s" % "\n".join("- %s %s" % (short, subject) for _, short, subject in commits)
        queue_comment(top, issue, "landed", body, k)
    code = replay(top)
    return 2 if failed else code


def main(argv):
    if argv != ["replay"] and not (len(argv) == 2 and argv[0] == "close-landed" and SHA.fullmatch(argv[1])):
        return entry.refuse(usage=USAGE)
    top = root()
    if top is None:
        return entry.refuse("github-queue.sh: no main working tree")
    return replay(top) if argv == ["replay"] else close_landed(top, argv[1])


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])

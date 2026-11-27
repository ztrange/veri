"""github-outage.sh: the dev session's local mode during a GitHub outage, run in-process.

Local mode is the file `.tdd/github-outage` in the repository's main working tree (found from any worktree through
git's common directory): GitHub status lines, then the held PR urls, then the marker line, then more held urls. Above
the marker are PRs held because their merge failed, in the order they failed; below it, reviewed runs' PRs, in the
order they were held. A PR url is a line that is exactly `https://…/pull/<digits>`; a trailing `\\r` is stripped and a
last line without a newline counts. `.tdd/github-outage-merging` lists the PRs taken off the file whose merge has not
been settled, each with its claimer's pid and start time. Every verb takes an exclusive lock on
`.tdd/github-outage.lock`, a file never removed, then reads both files afresh, so a file removed and re-created while
a verb waits on the lock is the file it acts on; each file is replaced by renaming a temporary file. The status read
runs in-process through `github_status`; the one wait per main working tree is `github-status.sh wait 3600`, started
detached, its record `.tdd/github-outage-wait` (`<nonce> <pid> <start>`) and its exit record
`.tdd/github-outage-wait.exit` (`<nonce> <code>`)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import fcntl
import os
import re
import subprocess
import sys
import time

import detach
import entry
import git
import github_status
import paths
import pid_file

USAGE = ("usage: github-outage.sh enter <pr-url> | hold <pr-url> | take --pid <pid> | adopt --pid <pid>\n"
         "       github-outage.sh settle <pr-url> merged|failed|released | wait-start | wait-status\n"
         "       github-outage.sh wait [<max-seconds>] | status [--pid <pid>]")
PR = re.compile(r"https://\S+/pull/[0-9]+")
MARKER = "-- held after review --"
FILE, MERGING, LOCK = ".tdd/github-outage", ".tdd/github-outage-merging", ".tdd/github-outage.lock"
WAIT, WAIT_EXIT, WAIT_OUT = ".tdd/github-outage-wait", ".tdd/github-outage-wait.exit", ".tdd/github-outage-wait.out"
WAIT_SECONDS = 3600
POLL_SECONDS = 5
WRAPPER = 'n=$1; shift; "$@"; rc=$?; echo "$n $rc" > "$0.tmp"; mv "$0.tmp" "$0"'


class World:
    """What the verbs ask of the outside; a case swaps any of these."""

    def status(self):
        """(code, lines) of one status read, github-status.sh's default components; NoAnswer when none."""
        return github_status.default_read()

    def alive(self, pid, start):
        """Whether <pid> answers kill -0 and was started at <start> (`pid_file.started_utc`'s text)."""
        try:
            os.kill(int(pid), 0)
        except (OSError, OverflowError, ValueError):
            return False
        return bool(start) and pid_file.started_utc(pid) == start

    def started(self, pid):
        return pid_file.started_utc(pid)

    def start(self, argv, out):
        with open(out, "w") as handle:
            return detach.start(argv, subprocess.DEVNULL, handle, handle)

    def nonce(self):
        return "%d.%d" % (time.time_ns(), os.getpid())

    def clock(self):
        return time.monotonic()

    def pause(self, seconds):
        time.sleep(seconds)


def is_pr(line):
    return PR.fullmatch(line) is not None


def lines_of(path):
    """The file's lines, a last line without newline kept; None when the file does not exist.

    Read in universal-newlines mode, so `\\r\\n` and a lone `\\r` end a line like `\\n`."""
    try:
        with open(path) as handle:
            return handle.read().splitlines()
    except FileNotFoundError:
        return None


def write(path, lines):
    temporary = "%s.tmp.%d" % (path, os.getpid())
    with open(temporary, "w") as handle:
        handle.write("".join(line + "\n" for line in lines))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def acquire(handle):
    fcntl.flock(handle, fcntl.LOCK_EX)


@contextlib.contextmanager
def locked(root):
    os.makedirs(os.path.join(root, ".tdd"), exist_ok=True)
    with open(os.path.join(root, LOCK), "a") as handle:
        acquire(handle)
        yield


def held(lines):
    return [line for line in lines if is_pr(line)]


def merging_of(root):
    """[(url, pid, start)] of the merging list, in order."""
    found = []
    for line in lines_of(os.path.join(root, MERGING)) or []:
        fields = line.split("\t")
        if is_pr(fields[0]):
            found.append((fields[0], fields[1] if len(fields) > 1 else "", fields[2] if len(fields) > 2 else ""))
    return found


def write_merging(root, entries):
    path = os.path.join(root, MERGING)
    if entries:
        write(path, ["\t".join(entry_) for entry_ in entries])
    elif os.path.exists(path):
        os.unlink(path)


def hold_first(lines, url):
    """`lines` with `url` held after the PRs already held because their merge failed (just above the marker)."""
    if url in lines:
        return lines
    at = lines.index(MARKER) if MARKER in lines else len(lines)
    return lines[:at] + [url] + lines[at:]


def enter(root, url, world):
    """A failed merge: read GitHub's status; on a counting incident hold `url` (creating the file when absent)."""
    if not is_pr(url):
        return 2, ["not a PR url: %s" % url]
    try:
        code, status = world.status()
    except github_status.NoAnswer as cause:
        return 2, ["no answer from GitHub's status page: %s" % cause]
    if code != 1:
        return 1, ["unexplained"] + [line for line in status if line != "up"]
    with locked(root):
        path = os.path.join(root, FILE)
        lines = lines_of(path)
        word = "entered" if lines is None else "held"
        write(path, status + [url, MARKER] if lines is None else hold_first(lines, url))
        write_merging(root, [entry_ for entry_ in merging_of(root) if entry_[0] != url])
    return 0, [word] + status


def hold(root, url):
    """A reviewed run's PR, held at the end; 3 when local mode is off."""
    if not is_pr(url):
        return 2, ["not a PR url: %s" % url]
    with locked(root):
        path = os.path.join(root, FILE)
        lines = lines_of(path)
        if lines is None:
            return 3, []
        if url not in lines:
            write(path, lines + [url])
    return 0, ["held"]


def take(root, pid, world):
    """The claim: the first held PR moves to the merging list under <pid>; `ended` once nothing is held or merging."""
    with locked(root):
        path = os.path.join(root, FILE)
        lines = lines_of(path)
        if lines is None:
            return 3, []
        merging = merging_of(root)
        busy = {entry_[0] for entry_ in merging}
        urls = [url for url in held(lines) if url not in busy]
        taken = urls[:1]
        if taken:
            write_merging(root, merging + [(taken[0], str(pid), world.started(pid))])
        kept = [line for line in lines if line not in busy and line not in taken]
        if kept != lines:
            write(path, kept)
        if taken:
            return 0, taken
        if merging:
            return 3, []
        os.unlink(path)
    return 0, ["ended"]


def settle(root, url, how):
    """A taken PR's merge is over: `merged` or `released` drops it; `failed` holds it again, first."""
    with locked(root):
        merging = merging_of(root)
        if url not in [entry_[0] for entry_ in merging]:
            return 3, []
        if how == "failed":
            path = os.path.join(root, FILE)
            write(path, hold_first(lines_of(path) or [MARKER], url))
        write_merging(root, [entry_ for entry_ in merging if entry_[0] != url])
    return 0, [how]


def adopt(root, pid, world):
    """Re-claim under <pid> each merging PR whose claimer is dead, or is <pid> itself from before a reset."""
    with locked(root):
        mine = world.started(pid)
        merging, adopted = [], []
        for url, claimer, start in merging_of(root):
            if (claimer == str(pid) and start == mine) or not world.alive(claimer, start):
                adopted.append(url)
                merging.append((url, str(pid), mine))
            else:
                merging.append((url, claimer, start))
        if adopted:
            write_merging(root, merging)
    return (0, adopted) if adopted else (3, [])


def wait_state(root, world):
    """`live`, `ended <code>` or `none` for the main working tree's wait."""
    record = (lines_of(os.path.join(root, WAIT)) or [""])[0].split(" ", 2)
    if len(record) != 3:
        return "none"
    nonce, pid, start = record
    finished = (lines_of(os.path.join(root, WAIT_EXIT)) or [""])[0].split(" ")
    if len(finished) == 2 and finished[0] == nonce:
        return "ended " + finished[1]
    return "live" if world.alive(pid, start) else "none"


def wait_start(root, world):
    """Start the one wait when local mode is on and no wait is live; two starters start one."""
    with locked(root):
        if lines_of(os.path.join(root, FILE)) is None:
            return 3, ["off"]
        if wait_state(root, world) == "live":
            return 3, ["live"]
        nonce = world.nonce()
        shim = os.path.join(paths.scripts_of(__file__), "github-status.sh")
        pid = world.start(["sh", "-c", WRAPPER, os.path.join(root, WAIT_EXIT), nonce, shim, "wait", str(WAIT_SECONDS)],
                          os.path.join(root, WAIT_OUT))
        write(os.path.join(root, WAIT), ["%s %s %s" % (nonce, pid, world.started(pid))])
    return 0, ["started"]


def wait_status(root, world):
    state = wait_state(root, world)
    return (3 if state == "none" else 0), [state]


def wait(root, max_seconds, poll, world):
    """Block until the wait ends (0, `ended <code>`), is found not live (2, `none`) or `max_seconds` pass (3)."""
    deadline = world.clock() + max_seconds
    while True:
        state = wait_state(root, world)
        if state != "live":
            return (0 if state.startswith("ended") else 2), [state]
        if world.clock() >= deadline:
            return 3, ["live"]
        world.pause(poll)


def status(root, world, pid=None):
    """What a starting session, a handoff and the check read: mode, held PRs, merging PRs, the wait.

    With <pid>, a merging PR that <pid> claimed (same start time) reads `mine` rather than `live`."""
    with locked(root):
        lines = lines_of(os.path.join(root, FILE))
        merging = merging_of(root)
    busy = {entry_[0] for entry_ in merging}
    out = ["mode " + ("on" if lines is not None else "off")]
    out += ["held " + url for url in held(lines or []) if url not in busy]
    mine = world.started(pid) if pid else None

    def claim(claimer, start):
        if pid and claimer == str(pid) and start == mine:
            return "mine"
        return "live" if world.alive(claimer, start) else "orphan"

    out += ["merging %s %s" % (url, claim(claimer, start)) for url, claimer, start in merging]
    out.append("wait " + wait_state(root, world))
    return (0 if lines is not None or merging else 3), out


def main_tree():
    return os.path.dirname(git.out("rev-parse", "--path-format=absolute", "--git-common-dir"))


def run(argv, root, world):
    verb, rest = (argv[0], argv[1:]) if argv else ("", [])
    if verb in ("enter", "hold") and len(rest) == 1:
        return enter(root, rest[0], world) if verb == "enter" else hold(root, rest[0])
    if verb in ("take", "adopt") and len(rest) == 2 and rest[0] == "--pid" and entry.whole_number(rest[1]):
        return take(root, rest[1], world) if verb == "take" else adopt(root, rest[1], world)
    if verb == "settle" and len(rest) == 2 and rest[1] in ("merged", "failed", "released") and is_pr(rest[0]):
        return settle(root, rest[0], rest[1])
    if verb == "status" and len(rest) == 2 and rest[0] == "--pid" and entry.whole_number(rest[1]):
        return status(root, world, rest[1])
    if verb in ("wait-start", "wait-status", "status") and not rest:
        return {"wait-start": wait_start, "wait-status": wait_status, "status": status}[verb](root, world)
    if verb == "wait" and len(rest) <= 1 and (not rest or entry.whole_number(rest[0])):
        return wait(root, int(rest[0]) if rest else WAIT_SECONDS + 60, POLL_SECONDS, world)
    return None


def main(argv):
    try:
        root = main_tree()
    except git.GitFailed as failed:
        return entry.refuse("github-outage.sh: no main working tree: %s" % failed)
    answer = run(argv, root, World())
    if answer is None:
        return entry.refuse(usage=USAGE)
    code, lines = answer
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])

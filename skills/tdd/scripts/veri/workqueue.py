"""workqueue.sh's subcommands, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import locale
import os
import re
import subprocess
import sys
import time

import blocked_by
import entry
import pid_file
import run_dir
import tunables
from github import NoAnswer, gh_json
from json_documents import items

USAGE = """workqueue.sh: usage: workqueue.sh assign <worker> <issue>...
                     workqueue.sh next <worker>
                     workqueue.sh start <worker> <issue>
                     workqueue.sh done <worker> <issue> <merge-sha>
                     workqueue.sh park <worker> <issue> <reason>
                     workqueue.sh show [<worker>]
"""


def queue_path():
    try:
        tree = run_dir.main_tree()
    except run_dir.NoMainTree:
        tree = ""
    if not tree:
        sys.stderr.write("workqueue.sh: outside a repository\n")
        raise SystemExit(2)
    return run_dir.main_file(tree, "workqueue")


def lock_tries():
    wait = tunables.get("VERI_WORKQUEUE_LOCK_WAIT", unless_empty=True)
    tries = entry.whole_number(wait, 0)
    if tries is not None:
        return tries * 20
    sys.stderr.write("workqueue.sh: VERI_WORKQUEUE_LOCK_WAIT must be a whole number >= 0: %s\n" % wait)
    raise SystemExit(2)


def unbound(name):
    sys.stderr.write("workqueue.sh: %s: unbound variable\n" % name)
    raise SystemExit(1)


def take_lock(lock):
    try:
        os.makedirs(os.path.dirname(lock), exist_ok=True)
    except OSError as error:
        sys.stderr.write("mkdir: %s: %s\n" % (error.filename, error.strerror))
        raise SystemExit(1) from error
    tries = lock_tries()
    while True:
        try:
            os.mkdir(lock)
        except FileExistsError:
            pass
        else:
            try:
                pid_file.record(holder_path(lock), os.getpid(), atomic=True)
            except BaseException:
                release_lock(lock)
                raise
            return
        if tries <= 0:
            sys.stderr.write("workqueue.sh: could not take the lock %s; %s\n" % (lock, holder_of(lock)))
            raise SystemExit(2)
        tries -= 1
        time.sleep(0.05)


def holder_path(lock):
    return os.path.join(lock, "holder")


def holder_of(lock):
    """`holder <pid> alive` or `holder <pid> dead` for the pid the lock's holder file records, `holder unrecorded`
    when it records none. A live pid whose start time differs from the recorded one is a reused pid: dead."""
    pid = pid_file.number_in(holder_path(lock))
    if pid is None:
        return "holder unrecorded"
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return "holder %s dead" % pid
    except PermissionError:
        pass
    try:
        matches = pid_file.start_matches(holder_path(lock), pid)
    except OSError:
        matches = False
    if not matches:
        return "holder %s dead" % pid
    return "holder %s alive" % pid


def release_lock(lock):
    with contextlib.suppress(FileNotFoundError):
        os.remove(holder_path(lock))
    os.rmdir(lock)


def origin_slug():
    url = subprocess.run(["git", "remote", "get-url", "origin"],
                         capture_output=True, text=True).stdout.rstrip("\n").removesuffix(".git")
    match = re.search(r"[:/]([^/:]+/[^/]+)$", url)
    return match.group(1) if match else ""


def next_item(argv):
    try:
        listing = gh_json("issues.json", "repos/{owner}/{repo}/issues?state=all&per_page=100")
    except NoAnswer:
        return 2
    issues = items(listing)
    worker = argv[1]
    repo = origin_slug()
    open_issues = {i["number"] for i in issues if i.get("state", "").upper() == "OPEN"}
    bodies = {i["number"]: i.get("body") or "" for i in issues}
    with open(queue_path()) as lines:
        for line in lines:
            owner, issue, state = line.rstrip("\n").split("\t")[:3]
            if owner != worker or state != "queued":
                continue
            if all(n not in open_issues for n in blocked_by.blockers(bodies.get(int(issue), ""), repo)):
                print(issue)
                return 0
    return 3


AWK_ESCAPES = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v"}


def awk_unescape(value):
    def one(match):
        code = match.group(1)
        if code[0] in "0123456789":
            number = 0
            for digit in code:
                number = number * 8 + int(digit)
            return chr(number % 256)
        return AWK_ESCAPES.get(code, code)
    return re.sub(r"\\([0-9]{1,3}|.)", one, value).partition("\0")[0]


def show(queue, argv):
    only = awk_unescape("".join(argv[1:2]))
    try:
        with open(queue, newline="\n") as lines:
            records = lines.read()
    except OSError:
        sys.stderr.write("awk: can't open file %s\n source line number 1\n" % queue)
        return 2
    grouped = {}
    for record in records.removesuffix("\n").split("\n") if records else []:
        fields = record.split("\t") + ["", ""]
        if only and fields[0] != only:
            continue
        grouped.setdefault(fields[0], []).append("\t%s\t%s\n" % (fields[1], fields[2]))
    for worker, entries in grouped.items():
        sys.stdout.write(worker + "\n" + "".join(entries))
    return 0


MOVES = {"start": ("queued", "running"), "done": ("running", "merged"), "park": ("running", "parked")}


def line_fields(line):
    return re.split(r"\t+", line.removesuffix("\n").strip("\t"), maxsplit=3) + ["", "", "", ""]


def read_fields(lines):
    for line in lines:
        if not line.endswith("\n"):
            return
        yield line_fields(line)


def move(queue, argv, fourth, source, target):
    detail = fourth if source == "running" else ""
    tmp = "%s.tmp.%d" % (queue, os.getpid())
    moved = False
    try:
        lines = open(queue, newline="\n")
    except OSError as error:
        sys.stderr.write("workqueue.sh: %s: %s\n" % (queue, error.strerror))
        return 1
    with lines, open(tmp, "w") as rewritten:
        for fields in map(line_fields, lines):
            if fields[0] == argv[1]:
                if fields[1:3] == [argv[2], source]:
                    fields[2:4] = [target, detail]
                    moved = True
            rewritten.write("\t".join(fields[:4]) + "\n")
    if not moved:
        os.remove(tmp)
        sys.stderr.write("workqueue.sh: %s holds no %s item for issue %s\n" % (argv[1], source, argv[2]))
        return 1
    status = subprocess.run(["mv", tmp, queue]).returncode
    return entry.to_contract(status)


def held_issue(queue, issues):
    if not os.path.isfile(queue):
        return None
    with open(queue, newline="\n") as lines:
        for fields in read_fields(lines):
            if fields[2] not in ("queued", "running"):
                continue
            if fields[1] in issues:
                return fields[1], fields[2]
    return None


def main(argv):
    try:
        return locked_main(argv)
    except SystemExit as stop:
        return stop.code


def locked_main(argv):
    command = argv[0] if argv else ""
    if command == "next":
        return next_item(argv)
    if (command in MOVES or command == "assign") and len(argv) < 3:
        return entry.refuse(usage=USAGE)
    fourth = "".join(argv[3:4])
    if command == "done" and not fourth:
        return entry.refuse(usage=USAGE)
    if command == "park":
        if "\t" in fourth or "\n" in fourth:
            return entry.refuse("workqueue.sh: a park reason may not hold a tab or a newline", usage=USAGE)
        if len(argv) < 4:
            return entry.refuse(usage=USAGE)
    if command == "assign":
        named = set()
        for issue in argv[2:]:
            if not issue:
                return entry.refuse("workqueue.sh: an issue argument is empty", usage=USAGE)
            if issue in named:
                return entry.refuse("workqueue.sh: issue %s is named twice" % issue, usage=USAGE)
            named.add(issue)
    if command not in MOVES and command not in ("assign", "show"):
        return entry.refuse("workqueue.sh: unknown subcommand: " + command, usage=USAGE)
    queue = queue_path()
    if command == "show":
        return show(queue, argv)
    lock = queue + ".lock"
    take_lock(lock)
    try:
        if command in MOVES:
            return move(queue, argv, fourth, *MOVES[command])
        held = held_issue(queue, argv[2:])
        if held:
            sys.stderr.write("workqueue.sh: issue %s is already %s\n" % held)
            return 2
        with open(queue, "a+b") as appended:
            if appended.tell():
                appended.seek(-1, os.SEEK_END)
                if appended.read(1) != b"\n":
                    appended.write(b"\n")
            encoding = locale.getpreferredencoding(False)
            for issue in argv[2:]:
                appended.write(
                    ("%s\t%s\tqueued\t\n" % (argv[1], issue)).encode(encoding))
        return 0
    finally:
        release_lock(lock)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])

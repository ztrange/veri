"""workqueue.sh's subcommands, run in-process."""
import os
import re
import subprocess
import sys
import time

import blocked_by
from github import NoAnswer, gh_json
from json_documents import items

USAGE = """workqueue.sh: usage: workqueue.sh assign <worker> <issue>...
                     workqueue.sh next <worker>
                     workqueue.sh start <worker> <issue>
                     workqueue.sh done <worker> <issue> <merge-sha>
                     workqueue.sh park <worker> <issue> <reason>
                     workqueue.sh show [<worker>]
"""


def refuse(message=None):
    if message is not None:
        sys.stderr.write(message + "\n")
    sys.stderr.write(USAGE)
    return 2


def main_working_tree():
    listing = subprocess.run(["git", "worktree", "list", "--porcelain"],
                             capture_output=True, text=True).stdout
    first = listing.split("\n", 1)[0]
    return first.removeprefix("worktree ")


def queue_path():
    return main_working_tree() + "/.tdd/workqueue"


class Abandoned(Exception):
    pass


def lock_tries():
    wait = os.environ.get("VERI_WORKQUEUE_LOCK_WAIT") or "30"
    if re.fullmatch(r"0[0-7]*", wait):
        return int(wait, 8) * 20
    if re.fullmatch(r"[1-9][0-9]*", wait):
        return int(wait) * 20
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", wait):
        unbound(wait)
    raise Abandoned


def unbound(name):
    sys.stderr.write("workqueue.sh: %s: unbound variable\n" % name)
    raise SystemExit(1)


def take_lock(lock):
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    tries = lock_tries()
    while True:
        try:
            os.mkdir(lock)
            return
        except FileExistsError:
            pass
        if tries <= 0:
            sys.stderr.write("workqueue.sh: could not take the lock %s\n" % lock)
            raise SystemExit(2)
        tries -= 1
        time.sleep(0.05)


def release_lock(lock):
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


MOVES = {"start": ("queued", "running"), "done": ("running", "merged"), "park": ("running", "parked")}


def move(queue, argv, source, target):
    detail = "".join(argv[3:4]) if source == "running" else ""
    tmp = "%s.tmp.%d" % (queue, os.getpid())
    moved = False
    try:
        lines = open(queue, newline="\n")
    except OSError as error:
        sys.stderr.write("workqueue.sh: %s: %s\n" % (queue, error.strerror))
        return 1
    with lines, open(tmp, "w") as rewritten:
        for line in lines:
            if not line.endswith("\n"):
                break
            fields = re.split(r"\t+", line[:-1].strip("\t"), maxsplit=3) + ["", "", "", ""]
            if len(argv) < 2:
                unbound("$2")
            if fields[0] == argv[1] and len(argv) < 3:
                unbound("$3")
            if fields[0] == argv[1] and fields[1:3] == [argv[2], source]:
                fields[2:4] = [target, detail]
                moved = True
            rewritten.write("\t".join(fields[:4]) + "\n")
    if not moved:
        os.remove(tmp)
        if len(argv) < 3:
            unbound("$%d" % (len(argv) + 1))
        sys.stderr.write("workqueue.sh: %s holds no %s item for issue %s\n" % (argv[1], source, argv[2]))
        return 1
    status = subprocess.run(["mv", tmp, queue]).returncode
    return status if 0 <= status <= 3 else 2


def main(argv):
    try:
        return locked_main(argv)
    except SystemExit as stop:
        return stop.code


def locked_main(argv):
    command = argv[0] if argv else ""
    if command == "next":
        return next_item(argv)
    if command == "done" and not "".join(argv[3:4]):
        return refuse()
    if command == "park":
        if "\t" in "".join(argv[3:4]) or "\n" in "".join(argv[3:4]):
            return refuse("workqueue.sh: a park reason may not hold a tab or a newline")
        if len(argv) < 4:
            unbound("$4")
    if command == "assign":
        named = set()
        for issue in argv[2:]:
            if issue in named:
                return refuse("workqueue.sh: issue %s is named twice" % issue)
            named.add(issue)
    queue = queue_path()
    lock = queue + ".lock"
    locked = False
    try:
        if command in MOVES or command == "assign":
            try:
                take_lock(lock)
                locked = True
            except Abandoned:
                if command != "assign":
                    return refuse("workqueue.sh: unknown subcommand: " + command)
        if command in MOVES:
            return move(queue, argv, *MOVES[command])
        if command != "assign":
            return refuse("workqueue.sh: unknown subcommand: " + command)
        with open(queue, "a") as appended:
            for issue in argv[2:]:
                appended.write("%s\t%s\tqueued\t\n" % (argv[1], issue))
        return 0
    finally:
        if locked:
            release_lock(lock)

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
        sys.stderr.write("workqueue.sh: %s: unbound variable\n" % wait)
        raise SystemExit(1)
    raise Abandoned


def take_lock(lock):
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
    if command == "assign":
        named = set()
        for issue in argv[2:]:
            if issue in named:
                return refuse("workqueue.sh: issue %s is named twice" % issue)
            named.add(issue)
    lock = queue_path() + ".lock"
    locked = False
    try:
        if command in ("start", "done", "park", "assign"):
            try:
                take_lock(lock)
                locked = True
            except Abandoned:
                if command != "assign":
                    return refuse("workqueue.sh: unknown subcommand: " + command)
        if command == "start":
            with open(queue_path()) as lines:
                for line in lines:
                    if line.split("\t")[:3] == [argv[1], argv[2], "queued"]:
                        break
                else:
                    sys.stderr.write("workqueue.sh: %s holds no queued item for issue %s\n" % (argv[1], argv[2]))
                    return 1
        if command != "assign":
            return refuse("workqueue.sh: unknown subcommand: " + command)
        with open(queue_path(), "a") as queue:
            for issue in argv[2:]:
                queue.write("%s\t%s\tqueued\t\n" % (argv[1], issue))
        return 0
    finally:
        if locked:
            release_lock(lock)

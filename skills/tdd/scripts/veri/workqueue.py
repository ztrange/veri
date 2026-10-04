"""workqueue.sh's subcommands, run in-process."""
import re
import subprocess
import sys

import blocked_by
from github import gh_json
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


def origin_slug():
    url = subprocess.run(["git", "remote", "get-url", "origin"],
                         capture_output=True, text=True).stdout.rstrip("\n").removesuffix(".git")
    match = re.search(r"[:/]([^/:]+/[^/]+)$", url)
    return match.group(1) if match else ""


def next_item(worker):
    issues = items(gh_json("issues.json", "repos/{owner}/{repo}/issues?state=all&per_page=100"))
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
    command = argv[0] if argv else ""
    if command == "next":
        return next_item(argv[1])
    if command == "done" and not "".join(argv[3:4]):
        return refuse()
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
    named = set()
    for issue in argv[2:]:
        if issue in named:
            return refuse("workqueue.sh: issue %s is named twice" % issue)
        named.add(issue)

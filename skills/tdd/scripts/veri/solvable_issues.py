"""solvable-issues.sh's selection, run in-process."""
import os
import re
import subprocess
import sys

import blocked_by
from github import NoAnswer, gh_json, gh_json_page
from json_documents import items

USAGE = "usage: solvable-issues.sh [--repo owner/name]"
PAGE_SIZE = 100
OLDEST_FIRST = "?state=all&sort=created&direction=asc&per_page=%d" % PAGE_SIZE
OPEN_PAGE = "?state=open&per_page=%d" % PAGE_SIZE


def main_working_tree():
    try:
        answer = subprocess.run(["git", "worktree", "list", "--porcelain"],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout
    except OSError:
        return ""
    return answer.split("\n", 1)[0].removeprefix("worktree ")


def in_flight(main_tree, number):
    if not main_tree:
        return False
    try:
        with open(os.path.join(main_tree, ".tdd", "wt", str(number), ".tdd", "conductor.pid")) as lock:
            pid = int(lock.read().strip())
    except (OSError, ValueError):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        pass
    return True


def refused_if_empty(name):
    if os.environ.get(name) == "":
        print("solvable-issues: %s is set but empty: name a label or leave it unset" % name, file=sys.stderr)
        return True
    return False


def is_open(entry):
    return entry.get("state", "").upper() == "OPEN"


def carries(issue, label):
    return any(entry["name"] == label for entry in issue.get("labels", []))


def open_listing(fixture, path, *args):
    listing = gh_json_page(fixture, path + OPEN_PAGE, *args)
    if len(items(listing)) >= PAGE_SIZE:
        listing = gh_json(fixture, path + OLDEST_FIRST, *args)
    return listing


def main(argv):
    repo = "".join(argv[1:2]) if argv[:1] == ["--repo"] else None
    if repo == "":
        print(USAGE, file=sys.stderr)
        return 2
    if refused_if_empty("VERI_LABEL") or refused_if_empty("VERI_PRIORITY_LABEL"):
        return 2
    label = os.environ.get("VERI_LABEL", "ready-for-agent")
    priority = os.environ.get("VERI_PRIORITY_LABEL", "priority")
    scope = ["--repo", repo] if repo else []
    prefix = "repos/%s" % (repo or "{owner}/{repo}")
    try:
        issues = open_listing("issues.json", prefix + "/issues",
                              "issue", "list", "--limit", "10000", "--json", "number,title,labels,body,state", *scope)
        prs = open_listing("prs.json", prefix + "/pulls", "pr", "list", "--limit", "10000", "--json", "body,state", *scope)
    except NoAnswer:
        return 2
    issues = [issue for issue in items(issues) if "pull_request" not in issue]
    claimed = {int(n) for pr in items(prs) if is_open(pr) for n in re.findall(r"\bCloses #(\d+)", pr["body"] or "")}
    open_issues = {issue["number"] for issue in issues if is_open(issue)}
    main_tree = main_working_tree()
    survivors = [issue for issue in issues
                 if is_open(issue) and carries(issue, label) and issue["number"] not in claimed
                 and not in_flight(main_tree, issue["number"])
                 and all(n not in open_issues for n in blocked_by.blockers(issue.get("body") or "", repo or ""))]
    if not survivors:
        return 3
    for issue in sorted(survivors, key=lambda issue: (0 if carries(issue, priority) else 1 if carries(issue, "bug") else 2,
                                                       issue["number"])):
        print(issue["number"])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

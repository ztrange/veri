"""solvable-issues.sh's selection, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import paths
import pid_file
import re
import subprocess
import sys

import blocked_by
import tunables
from github import NoAnswer, gh_json, gh_json_page
from json_documents import items

USAGE = "usage: solvable-issues.sh [--repo owner/name] [--not-running]"
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
    return bool(pid_file.live_conductor(os.path.join(main_tree, ".tdd", "wt", str(number))))


def refused_if_empty(name):
    if tunables.read(name, None) == "":
        print("solvable-issues: %s is set but empty: name a label or leave it unset" % name, file=sys.stderr)
        return True
    return False


def scope_label():
    """The opt-in label, or None when VERI_LABEL is set but empty."""
    if refused_if_empty("VERI_LABEL"):
        return None
    return tunables.read("VERI_LABEL", "ready-for-agent")


def priority_label():
    """The priority label, or None when VERI_PRIORITY_LABEL is set but empty."""
    if refused_if_empty("VERI_PRIORITY_LABEL"):
        return None
    return tunables.read("VERI_PRIORITY_LABEL", "priority")


def band(issue, priority):
    """An issue's selection band: priority, then bugs the groom did not call low-risk, then the rest."""
    if carries(issue, priority):
        return 0
    return 1 if carries(issue, "bug") and not carries(issue, "low-risk") else 2


def is_open(entry):
    return entry.get("state", "").upper() == "OPEN"


def carries(issue, label):
    return any(entry["name"] == label for entry in issue.get("labels", []))


def open_listing(fixture, path, *args):
    listing = gh_json_page(fixture, path + OPEN_PAGE, *args)
    if len(items(listing)) >= PAGE_SIZE:
        listing = gh_json(fixture, path + OLDEST_FIRST, *args)
    return listing


def taken(issue):
    return any(entry["name"].startswith("taken:") for entry in issue.get("labels", []))


def solvable(label, priority="priority", repo=None):
    """(exit code, the solvable issue numbers in selection order) for the opt-in <label>; 2 for an unreadable listing."""
    try:
        return select(label, priority, repo)
    except json.JSONDecodeError:
        return 2, []


def solvable_in_scope():
    """(exit code, the solvable issue numbers) for the configured scope; 2 when a label is unusable."""
    label = scope_label()
    priority = label and priority_label()
    if label is None or priority is None:
        return 2, []
    return solvable(label, priority)


def select(label, priority="priority", repo=None):
    """(exit code, the solvable issue numbers in selection order) for the opt-in <label>."""
    scope = ["--repo", repo] if repo else []
    prefix = "repos/%s" % (repo or "{owner}/{repo}")
    try:
        issues = open_listing("issues.json", prefix + "/issues",
                              "issue", "list", "--limit", "10000", "--json", "number,title,labels,body,state", *scope)
        prs = open_listing("prs.json", prefix + "/pulls", "pr", "list", "--limit", "10000", "--json", "body,state", *scope)
    except NoAnswer:
        return 2, []
    issues = [issue for issue in items(issues) if "pull_request" not in issue]
    claimed = {int(n) for pr in items(prs) if is_open(pr) for n in re.findall(r"\bCloses #(\d+)", pr["body"] or "")}
    open_issues = {issue["number"] for issue in issues if is_open(issue)}
    main_tree = main_working_tree()
    survivors = [issue for issue in issues
                 if is_open(issue) and carries(issue, label) and not taken(issue) and not carries(issue, "parked") and issue["number"] not in claimed
                 and not in_flight(main_tree, issue["number"])
                 and all(n not in open_issues for n in blocked_by.blockers(issue.get("body") or "", repo or ""))]
    if not survivors:
        return 3, []
    return 0, [issue["number"] for issue in sorted(
        survivors, key=lambda issue: (band(issue, priority), issue["number"]))]


def running_numbers():
    scripts = paths.scripts_of(__file__)
    listing = subprocess.run(["ps", "-axo", "pid=,command="], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True).stdout
    found = [number for directory, number in re.findall(
        r"(?:^|\s)(\S+)/(?:run-conductor\.sh|veri/run_conductor\.py) (\d+)(?=\s|$)", listing, re.M)
        if os.path.realpath(directory) == os.path.realpath(scripts)]
    return {int(number) for number in found}


def main(argv):
    skip = set()
    rest = [word for word in argv if word != "--not-running"]
    if (argv.count("--not-running") > 1 or "--repo" in argv[:-1] and argv[argv.index("--repo") + 1] == "--not-running"
            or len(rest) not in (0, 2) or (rest and (rest[0] != "--repo" or rest[1] == ""))):
        print(USAGE, file=sys.stderr)
        return 2
    repo = rest[1] if rest else None
    if len(rest) != len(argv):
        main_tree = main_working_tree()
        starting = pid_file.starting_runs(main_tree)
        skip = running_numbers() | {int(number) for number in starting}
    label = scope_label()
    priority = label and priority_label()
    if label is None or priority is None:
        return 2
    code, numbers = select(label, priority, repo)
    numbers = [number for number in numbers if int(number) not in skip]
    for number in numbers:
        print(number)
    return code if numbers or code != 0 else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

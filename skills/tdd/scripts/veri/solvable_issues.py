"""solvable-issues.sh's selection, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import paths
import pid_file
import re
import run_dir
import sys

import blocked_by
import stack_branch
import tunables
from github import NoAnswer, closed_issues, gh_json, gh_json_page, joined_issues, pulls_in
from json_documents import items

USAGE = "usage: solvable-issues.sh [--repo owner/name] [--not-running]"
PAGE_SIZE = 100
OLDEST_FIRST = "?state=all&sort=created&direction=asc&per_page=%d" % PAGE_SIZE
OPEN_PAGE = "?state=open&per_page=%d" % PAGE_SIZE


def in_flight(main_tree, number):
    if not main_tree:
        return False
    return bool(pid_file.live_conductor(run_dir.worktree(main_tree, number)))


def refused_if_empty(name):
    if tunables.read(name, None) == "":
        print("solvable-issues: %s is set but empty: name a label or leave it unset" % name, file=sys.stderr)
        return True
    return False


def scope_label():
    """The opt-in label, or None when VERI_LABEL is set but empty."""
    if refused_if_empty("VERI_LABEL"):
        return None
    return tunables.get("VERI_LABEL")


def priority_label():
    """The priority label, or None when VERI_PRIORITY_LABEL is set but empty."""
    if refused_if_empty("VERI_PRIORITY_LABEL"):
        return None
    return tunables.get("VERI_PRIORITY_LABEL")


def band(issue, priority):
    """An issue's selection band: priority bugs, then priority, then bugs the groom did not call low-risk, then the rest."""
    if carries(issue, priority):
        return 0 if carries(issue, "bug") else 1
    return 2 if carries(issue, "bug") and not carries(issue, "low-risk") else 3


def is_open(entry):
    return entry.get("state", "").upper() == "OPEN"


def carries(issue, label):
    return any(entry["name"] == label for entry in issue.get("labels", []))


def open_listing(fixture, path, *args):
    listing = gh_json_page(fixture, path + OPEN_PAGE, *args)
    if len(items(listing)) >= PAGE_SIZE:
        listing = gh_json(fixture, path + OLDEST_FIRST, *args)
    return listing


def own_run_branch(pr, number):
    """Whether <pr> is issue <number>'s own run branch, tdd/<number>-…: a released run's PR, which claims nothing while a draft (its resume continues it) and claims again once readied."""
    return pr.head_ref.startswith("tdd/%s-" % number)


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


def inherit_bands(issues, blockers, bands):
    """Lift `bands` in place to the best band of each open issue's dependents; return {blocker: dependent that set it}."""
    origin = {}
    changed = True
    while changed:
        changed = False
        for issue in issues:
            if not is_open(issue):
                continue
            for n in blockers[issue["number"]]:
                if n in bands and bands[issue["number"]] < min(bands[n], 2):
                    bands[n] = bands[issue["number"]]
                    origin[n] = issue["number"]
                    changed = True
    return origin


def report_inherited(ordered, bands, origin):
    for issue in ordered:
        n = issue["number"]
        if n in origin:
            print("#%d inherits %s from #%d" % (n, ("priority bug", "priority")[bands[n]], origin[n]), file=sys.stderr)


def select(label, priority="priority", repo=None):
    """(exit code, the solvable issue numbers in selection order) for the opt-in <label>."""
    scope = ["--repo", repo] if repo else []
    prefix = "repos/%s" % (repo or "{owner}/{repo}")
    try:
        issues = open_listing("issues.json", prefix + "/issues",
                              "issue", "list", "--limit", "10000", "--json", "number,title,labels,body,state", *scope)
        prs = open_listing("prs.json", prefix + "/pulls", "pr", "list", "--limit", "10000", "--json", "body,state,headRefName,isDraft", *scope)
    except NoAnswer:
        return 2, []
    issues = [issue for issue in items(issues) if "pull_request" not in issue]
    claimed = {int(n) for pr in pulls_in(prs) if pr.state == "OPEN" for n in closed_issues(pr.body)
               if not own_run_branch(pr, n) or pr.draft is False}
    open_issues = {issue["number"] for issue in issues if is_open(issue)}
    blockers = {issue["number"]: blocked_by.blockers(issue.get("body") or "", repo or "") for issue in issues}
    bands = {issue["number"]: band(issue, priority) for issue in issues}
    origin = inherit_bands(issues, blockers, bands)
    main_tree = run_dir.main_tree(missing="")
    try:
        stack = stack_branch.named(main_tree or ".")
        if stack:
            claimed |= joined_issues(stack, repo)
    except stack_branch.Refused as refused:
        print("solvable-issues: %s" % refused, file=sys.stderr)
        return 2, []
    except NoAnswer:
        return 2, []
    survivors = [issue for issue in issues
                 if is_open(issue) and carries(issue, label) and not taken(issue) and not carries(issue, "parked") and issue["number"] not in claimed
                 and not in_flight(main_tree, issue["number"])
                 and all(n not in open_issues for n in blockers[issue["number"]])]
    if not survivors:
        return 3, []
    ordered = sorted(survivors, key=lambda issue: (bands[issue["number"]], issue["number"]))
    report_inherited(ordered, bands, origin)
    return 0, [issue["number"] for issue in ordered]


def running_numbers():
    scripts = paths.scripts_of(__file__)
    listing = pid_file.listing(quiet=True)
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
        main_tree = run_dir.main_tree(missing="")
        starting = pid_file.runs_with_directory(main_tree)
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

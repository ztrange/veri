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
import git
import stack_branch
import tunables
from github import (ISSUE_AUTHOR_ASSOCIATIONS, NoAnswer, author_association, closed_issues, gh_json, gh_json_page,
                    joined_issues, pulls_in, trusted_author)
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


def author_label():
    """The label that takes a stranger's issue once read (PRD 022.4), or None when VERI_AUTHOR_LABEL is set but empty."""
    if refused_if_empty("VERI_AUTHOR_LABEL"):
        return None
    return tunables.get("VERI_AUTHOR_LABEL")


def author_read(issue, label):
    """Whether <issue>'s author may have it taken: an OWNER, MEMBER or COLLABORATOR (github.trusted_author), or it
    carries <label>, the operator's mark that a stranger's issue was read."""
    return trusted_author(issue, ISSUE_AUTHOR_ASSOCIATIONS) or carries(issue, label)


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


def github_repository(root):
    """`owner/name`, lower-cased, of the GitHub repository origin of <root> points at (an https, ssh or scp-style URL,
    `.git` dropped); None when there is no origin or its URL names no GitHub repository."""
    got = git.git("remote", "get-url", "origin", cwd=root, capture_output=True, text=True)
    if got.returncode != 0:
        return None
    found = re.fullmatch(r"(?:https://|ssh://git@|git@)github\.com[/:]([^/\s]+)/([^/\s]+?)(?:\.git)?/?",
                         got.stdout.strip())
    return ("%s/%s" % found.groups()).lower() if found else None


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


def scope_labels():
    """The (opt-in, priority, author) labels, or None when one of their variables is set but empty."""
    label = scope_label()
    priority = label and priority_label()
    author = priority and author_label()
    if label is None or priority is None or author is None:
        return None
    return label, priority, author


def solvable_in_scope():
    """(exit code, the solvable issue numbers) for the configured scope; 2 when a label is unusable."""
    labels = scope_labels()
    if labels is None:
        return 2, []
    label, priority, _ = labels
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
    author = tunables.get("VERI_AUTHOR_LABEL")
    scope = ["--repo", repo] if repo else []
    prefix = "repos/%s" % (repo or "{owner}/{repo}")
    try:
        # Over REST under every driver: gh issue list --json has no author_association, which the author rule reads.
        issues = open_listing("issues.json", prefix + "/issues")
        prs = open_listing("prs.json", prefix + "/pulls", "pr", "list", "--limit", "10000", "--json", "body,state,headRefName,isDraft,isCrossRepository", *scope)
    except NoAnswer:
        return 2, []
    issues = [issue for issue in items(issues) if "pull_request" not in issue]
    claimed = {int(n) for pr in pulls_in(prs) if pr.state == "OPEN" and not pr.cross_repository for n in closed_issues(pr.body)
               if not own_run_branch(pr, n) or pr.draft is False}
    open_issues = {issue["number"] for issue in issues if is_open(issue)}
    blockers = {issue["number"]: blocked_by.blockers(issue.get("body") or "", repo or "") for issue in issues}
    bands = {issue["number"]: band(issue, priority) for issue in issues}
    origin = inherit_bands(issues, blockers, bands)
    main_tree = run_dir.main_tree(missing="")
    try:
        stack = stack_branch.named(main_tree or ".")
        if stack and repo:
            local = github_repository(main_tree or ".")
            if local is None:
                print("solvable-issues: a stack branch is named, but origin of %s names no GitHub repository to compare"
                      " with --repo %s" % (main_tree or ".", repo), file=sys.stderr)
                return 2, []
            stack = stack if local == repo.lower() else None
        if stack:
            claimed |= joined_issues(stack, repo)
    except stack_branch.Refused as refused:
        print("solvable-issues: %s" % refused, file=sys.stderr)
        return 2, []
    except NoAnswer:
        return 2, []
    otherwise = [issue for issue in issues
                 if is_open(issue) and carries(issue, label) and not taken(issue) and not carries(issue, "parked") and not carries(issue, "draft") and issue["number"] not in claimed
                 and not in_flight(main_tree, issue["number"])
                 and all(n not in open_issues for n in blockers[issue["number"]])]
    survivors = [issue for issue in otherwise if author_read(issue, author)]
    for issue in otherwise:
        if not author_read(issue, author):
            print("solvable-issues: #%d skipped: its author is %s, not OWNER, MEMBER or COLLABORATOR; label it %s once read"
                  % (issue["number"], author_association(issue), author), file=sys.stderr)
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
    labels = scope_labels()
    if labels is None:
        return 2
    label, priority, _ = labels
    code, numbers = select(label, priority, repo)
    numbers = [number for number in numbers if int(number) not in skip]
    for number in numbers:
        print(number)
    return code if numbers or code != 0 else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

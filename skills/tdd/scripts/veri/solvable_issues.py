"""solvable-issues.sh's selection, run in-process."""
import os
import subprocess
import sys

from github import gh_json
from json_documents import items

USAGE = "usage: solvable-issues.sh [--repo owner/name]"


def main_working_tree():
    answer = subprocess.run(["git", "worktree", "list", "--porcelain"],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout
    return answer.split("\n", 1)[0].removeprefix("worktree ")


def in_flight(main_tree, number):
    return os.path.exists(os.path.join(main_tree, ".tdd", "wt", str(number), ".tdd", "conductor.pid"))


def refused_if_empty(name):
    if os.environ.get(name) == "":
        print("solvable-issues: %s is set but empty: name a label or leave it unset" % name, file=sys.stderr)
        return True
    return False


def carries(issue, label):
    return any(entry["name"] == label for entry in issue.get("labels", []))


def main(argv):
    repo = "".join(argv[1:2]) if argv[:1] == ["--repo"] else None
    if repo == "":
        print(USAGE, file=sys.stderr)
        return 2
    if refused_if_empty("VERI_LABEL") or refused_if_empty("VERI_PRIORITY_LABEL"):
        return 2
    label = os.environ.get("VERI_LABEL", "ready-for-agent")
    scope = ["--repo", repo] if repo else []
    prefix = "repos/%s" % (repo or "{owner}/{repo}")
    issues = items(gh_json("issues.json", prefix + "/issues",
                           "issue", "list", "--limit", "10000", "--json", "number,title,labels,body,state", *scope))
    gh_json("prs.json", prefix + "/pulls", "pr", "list", "--limit", "10000", "--json", "body,state", *scope)
    main_tree = main_working_tree()
    for issue in issues:
        if carries(issue, label) and not in_flight(main_tree, issue["number"]):
            print(issue["number"])
    return 0

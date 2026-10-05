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


def main(argv):
    if argv[:1] == ["--repo"] and not "".join(argv[1:2]):
        print(USAGE, file=sys.stderr)
        return 2
    issues = items(gh_json("issues.json", "repos/{owner}/{repo}/issues"))
    main_tree = main_working_tree()
    for issue in issues:
        if not in_flight(main_tree, issue["number"]):
            print(issue["number"])
    return 0

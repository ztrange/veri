"""solvable-issues.sh's selection, run in-process."""
import sys

from github import gh_json
from json_documents import items

USAGE = "usage: solvable-issues.sh [--repo owner/name]"


def main(argv):
    if argv[:1] == ["--repo"] and not "".join(argv[1:2]):
        print(USAGE, file=sys.stderr)
        return 2
    issues = items(gh_json("issues.json", "repos/{owner}/{repo}/issues"))
    for issue in issues:
        print(issue["number"])
    return 0

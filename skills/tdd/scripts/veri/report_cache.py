"""report-cache.sh's computations, run in-process."""
import datetime
import json
import os
import subprocess
import sys

USAGE = "usage: report-cache.sh refresh\n"
FIELDS = "number,title,state,labels,closedAt,updatedAt"


def main_tree():
    dot_git = os.path.join(os.getcwd(), ".git")
    if not os.path.isfile(dot_git):
        return os.getcwd()
    with open(dot_git) as pointer:
        gitdir = pointer.read().strip().split("gitdir:", 1)[1].strip()
    return os.path.dirname(os.path.dirname(os.path.dirname(gitdir)))


def refresh():
    done = subprocess.run(
        ["gh", "issue", "list", "--state", "all", "--limit", "100000", "--json", FIELDS],
        capture_output=True, text=True)
    issues = json.loads(done.stdout)
    fetched_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tdd = os.path.join(main_tree(), ".tdd")
    os.makedirs(tdd, exist_ok=True)
    with open(os.path.join(tdd, "report-cache.json"), "w") as out:
        json.dump({"fetched_at": fetched_at, "issues": issues}, out)
    return 0


def main(argv):
    if argv == ["refresh"]:
        return refresh()
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

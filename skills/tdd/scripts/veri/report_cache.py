"""report-cache.sh's computations, run in-process."""
import datetime
import json
import os
import subprocess
import sys

USAGE = "usage: report-cache.sh refresh\n"
FIELDS = "number,title,state,labels,closedAt,updatedAt"


def refresh():
    done = subprocess.run(
        ["gh", "issue", "list", "--state", "all", "--limit", "100000", "--json", FIELDS],
        capture_output=True, text=True)
    issues = json.loads(done.stdout)
    fetched_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(".tdd", exist_ok=True)
    with open(os.path.join(".tdd", "report-cache.json"), "w") as out:
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

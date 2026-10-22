"""report-cache.sh's computations, run in-process."""
import datetime
import json
import os
import re
import subprocess
import sys

USAGE = "usage: report-cache.sh refresh\n"
FIELDS = "number,title,state,labels,closedAt,updatedAt,body,comments"


def main_tree():
    dot_git = os.path.join(os.getcwd(), ".git")
    if not os.path.isfile(dot_git):
        return os.getcwd()
    with open(dot_git) as pointer:
        gitdir = pointer.read().strip().split("gitdir:", 1)[1].strip()
    return os.path.dirname(os.path.dirname(os.path.dirname(gitdir)))


def blocked_by(body):
    section = re.search(r"^## Blocked by\s*\n(.*?)(?=^## |\Z)", body or "", re.M | re.S)
    return [int(n) for n in re.findall(r"#(\d+)", section.group(1))] if section else []


def wall_seconds(comments):
    seconds = None
    for comment in comments or []:
        body = comment.get("body") or ""
        found = re.search(r"Wall time for the issue: (\d+) s", body)
        if re.search(r"^### 📊 Metrics", body, re.M) and found:
            seconds = int(found.group(1))
    return seconds


def refresh():
    tdd = os.path.join(main_tree(), ".tdd")
    path = os.path.join(tdd, "report-cache.json")
    kept = {}
    command = ["gh", "issue", "list", "--state", "all", "--limit", "100000", "--json", FIELDS]
    if os.path.exists(path):
        with open(path) as existing:
            before = json.load(existing)
        kept = {issue["number"]: issue for issue in before["issues"]}
        command += ["--search", "updated:>=" + before["fetched_at"]]
    done = subprocess.run(command, capture_output=True, text=True)
    issues = json.loads(done.stdout)
    for issue in issues:
        issue["blockedBy"] = blocked_by(issue.pop("body", ""))
        issue["wallSeconds"] = wall_seconds(issue.pop("comments", []))
        issue["lane"] = None
    kept.update({issue["number"]: issue for issue in issues})
    issues = list(kept.values())
    fetched_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(tdd, exist_ok=True)
    with open(path, "w") as out:
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

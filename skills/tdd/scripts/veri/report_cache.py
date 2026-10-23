"""report-cache.sh's computations, run in-process."""
import datetime
import json
import os
import re
import sys

import github

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


def last_metrics_field(comments, pattern):
    value = None
    for comment in comments or []:
        body = comment.get("body") or ""
        found = re.search(pattern, body, re.M)
        if re.search(r"^### 📊 Metrics", body, re.M) and found:
            value = found.group(1)
    return value


def wall_seconds(comments):
    seconds = last_metrics_field(comments, r"Wall time for the issue: (\d+) s")
    return None if seconds is None else int(seconds)


def lane(comments):
    return last_metrics_field(comments, r"^Lane: (\S+)")


def refresh():
    tdd = os.path.join(main_tree(), ".tdd")
    path = os.path.join(tdd, "report-cache.json")
    kept = {}
    command = ["--state", "all", "--limit", "100000", "--json", FIELDS]
    if os.path.exists(path):
        try:
            with open(path) as existing:
                before = json.load(existing)
        except json.JSONDecodeError as failure:
            sys.stderr.write("report-cache.sh: %s is unreadable (%s), rebuilding\n" % (path, failure))
        else:
            kept = {issue["number"]: issue for issue in before["issues"]}
            command += ["--search", "updated:>=" + before["fetched_at"]]
    try:
        issues = json.loads(github.gh_issue_list(*command))
    except github.NoAnswer as failure:
        sys.stderr.write("report-cache.sh: gh issue list failed: %s\n" % failure.answer)
        return 2
    for issue in issues:
        issue["blockedBy"] = blocked_by(issue.pop("body", ""))
        comments = issue.pop("comments", [])
        issue["wallSeconds"] = wall_seconds(comments)
        issue["lane"] = lane(comments)
    kept.update({issue["number"]: issue for issue in issues})
    issues = list(kept.values())
    fetched_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(tdd, exist_ok=True)
    temp = path + ".tmp"
    with open(temp, "w") as out:
        json.dump({"fetched_at": fetched_at, "issues": issues}, out)
    os.replace(temp, path)
    return 0


def main(argv):
    if argv == ["refresh"]:
        return refresh()
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

"""report-cache.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import os
import re
import sys
import tempfile
import time

import github
import tunables

USAGE = "usage: report-cache.sh refresh\n"
PAGE_SIZE = 100
SEARCH_CAP = 1000
CACHE_FORMAT = 2
FIELDS ="number,title,state,labels,closedAt,updatedAt,body,comments"


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


def read_issue_page(size, *search):
    attempts = int(tunables.read("VERI_PAGE_RETRIES", "3"))
    for attempt in range(attempts):
        try:
            args = ("--state", "all", "--limit", str(size), "--json", FIELDS) + search
            return json.loads(github.gh_issue_list(*args)), size
        except github.NoAnswer:
            if attempt == attempts - 1:
                raise
            size = max(1, size // 2)
            time.sleep(float(tunables.read("VERI_PAGE_RETRY_SLEEP", "2")))


def now_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_pages(since=None):
    bound = [since] if since else []
    first, size = read_issue_page(PAGE_SIZE, "--search", " ".join(bound + ["sort:updated-desc"]))
    if len(first) < size:
        return first
    seen = {}
    page = first
    while True:
        fresh = [issue for issue in page if issue["number"] not in seen]
        seen.update({issue["number"]: issue for issue in fresh})
        if len(page) < size:
            if len(page) >= SEARCH_CAP:
                raise github.NoAnswer("the search API capped a page at %d rows" % len(page))
            return list(seen.values())
        if fresh:
            search = " ".join(bound + ["sort:updated-desc updated:<="]) + min(issue["updatedAt"] for issue in page)
        else:
            size *= 2
        page, size = read_issue_page(size, "--search", search)


def refresh():
    tdd = os.path.join(main_tree(), ".tdd")
    path = os.path.join(tdd, "report-cache.json")
    kept = {}
    since = None
    if os.path.exists(path):
        try:
            with open(path) as existing:
                before = json.load(existing)
            search = "updated:>=" + before["fetched_at"]
            loaded = {issue["number"]: issue for issue in before["issues"]}
            current = before.get("format") == CACHE_FORMAT
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as failure:
            sys.stderr.write("report-cache.sh: %s is unreadable (%s), rebuilding\n" % (path, failure))
        else:
            kept = loaded if current else {}
            since = search if current else None
    fetched_at = now_stamp()
    try:
        issues = fetch_pages(since)
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
    os.makedirs(tdd, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=tdd, prefix="report-cache.json.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as out:
            json.dump({"format": CACHE_FORMAT, "fetched_at": fetched_at, "issues": issues}, out)
        os.replace(temp, path)
    except BaseException:
        os.unlink(temp)
        raise
    return 0


def main(argv):
    if argv == ["refresh"]:
        return refresh()
    sys.stderr.write(USAGE)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

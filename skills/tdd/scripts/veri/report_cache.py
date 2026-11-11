"""report-cache.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import calendar
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import github
import tunables

USAGE = "usage: report-cache.sh refresh\n"
PAGE_SIZE = 100
SEARCH_CAP = 1000
FIELDS = "number,title,state,labels,closedAt,updatedAt,body"


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


def links(own, body, comments):
    text = "\n".join([body or ""] + [c.get("body") or "" for c in comments or []])
    return sorted({int(n) for n in re.findall(r"#(\d+)", text)} - {own})


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


def fetch_comments():
    week_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    by_number = {}
    for search in ("PRD in:title", "closed:>=" + week_ago):
        args = ("--state", "all", "--limit", str(SEARCH_CAP), "--json", "number,comments", "--search", search)
        rows = json.loads(github.gh_issue_list(*args))
        if len(rows) >= SEARCH_CAP:
            raise github.NoAnswer("the comments search hit the %d-row cap" % SEARCH_CAP)
        for row in rows:
            by_number[row["number"]] = row.get("comments", [])
    return by_number


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


def since_time(root):
    try:
        with open(os.path.join(root, ".tdd", "status-last")) as last:
            return calendar.timegm(time.strptime(json.load(last)["time"], "%Y-%m-%dT%H:%M:%SZ"))
    except (OSError, ValueError, KeyError, TypeError):
        return None


def landed(root, since):
    if not os.path.exists(os.path.join(root, ".git", "HEAD")):
        return []
    fmt = "%(creatordate:unix)\t%(refname:short)\t%(creatordate:format-local:%Y-%m-%d %H:%M)\t%(contents:subject)"
    listed = subprocess.run(["git", "-C", root, "tag", "--list", "--format=" + fmt],
                            capture_output=True, text=True).stdout.splitlines()
    rows = [line.split("\t", 3) for line in listed]
    return [{"name": name, "date": date, "subject": subject}
            for created, name, date, subject in rows if since is None or int(created) >= since]


def refresh():
    tdd = os.path.join(main_tree(), ".tdd")
    path = os.path.join(tdd, "report-cache.json")
    kept = {}
    since = None
    stale = False
    if os.path.exists(path):
        try:
            with open(path) as existing:
                before = json.load(existing)
            search = "updated:>=" + before["fetched_at"]
            loaded = {issue["number"]: issue for issue in before["issues"]}
            if before.get("cache_format") != 2:
                search = None
            elif any("links" not in issue for issue in loaded.values()):
                stale = True
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as failure:
            sys.stderr.write("report-cache.sh: %s is unreadable (%s), rebuilding\n" % (path, failure))
        else:
            if not stale:
                kept = loaded
                since = search
    fetched_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        issues = fetch_pages(since)
        comments_by_number = fetch_comments()
    except github.NoAnswer as failure:
        sys.stderr.write("report-cache.sh: gh issue list failed: %s\n" % failure.answer)
        return 2
    if stale:
        sys.stderr.write("report-cache.sh: %s has issues without links, rebuilding\n" % path)
    for issue in issues:
        body = issue.pop("body", "")
        if re.match(r"PRD \d+", issue["title"]):
            issue["body"] = body
        comments = comments_by_number.get(issue["number"], [])
        issue["blockedBy"] = blocked_by(body)
        issue["links"] = links(issue["number"], body, comments)
        issue["wallSeconds"] = wall_seconds(comments)
        issue["lane"] = lane(comments)
    kept.update({issue["number"]: issue for issue in issues})
    issues = list(kept.values())
    os.makedirs(tdd, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=tdd, prefix="report-cache.json.", suffix=".tmp")
    try:
        root = os.path.dirname(tdd)
        since = since_time(root)
        with os.fdopen(fd, "w") as out:
            json.dump({"cache_format": 2, "fetched_at": fetched_at, "issues": issues,
                       "landed": landed(root, since), "since": since or 0}, out)
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

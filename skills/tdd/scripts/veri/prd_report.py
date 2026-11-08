"""report.sh's renderer, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import os
import re
import sys

import issue_worktree
import solvable_issues

USAGE = "usage: report.sh --report"
CACHE = ".tdd/report-cache.json"
OWED = ".tdd/report-owed.json"


def _utc(stamp):
    return datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def _prd_number(title):
    match = re.match(r"PRD (\d+)", title)
    return match.group(1) if match else None


def _heads(opened):
    heads = {}
    for issue in opened:
        number = _prd_number(issue["title"])
        if number:
            known = heads.get(number)
            if known is None or issue["number"] < known["number"]:
                heads[number] = issue
    return heads


def _load(path):
    with open(path) as f:
        return json.load(f)


def _stale(stored, nnn, issue):
    return stored.get(nnn, {}).get("updatedAt") != issue["updatedAt"]


def main(argv):
    if argv == ["--stale"]:
        snapshot = _load(CACHE)
        stored = _load(OWED)
        heads = _heads([o for o in snapshot["issues"] if o["state"] == "OPEN"])
        for nnn, issue in sorted(heads.items(), key=lambda p: int(p[0])):
            if _stale(stored, nnn, issue):
                print(nnn)
        return 0
    if argv == ["--report"]:
        if not os.path.exists(CACHE):
            print("no snapshot: %s is missing" % CACHE, file=sys.stderr)
            return 2
        with open(CACHE) as f:
            snapshot = json.load(f)
        now = datetime.datetime.now(datetime.timezone.utc)
        hours = int((now - _utc(snapshot["fetched_at"])).total_seconds() // 3600)
        print("snapshot age: %d hours" % hours)
        opened = [o for o in snapshot["issues"] if o["state"] == "OPEN"]
        open_numbers = {o["number"] for o in opened}
        stored = {}
        if os.path.exists(OWED):
            with open(OWED) as f:
                stored = json.load(f)
        heads = _heads(opened)
        for nnn, issue in sorted(heads.items(), key=lambda p: int(p[0])):
            print("PRD %s (#%d) — %s" % (nnn, issue["number"], issue["title"]))
            children = []
            for other in snapshot["issues"]:
                if other["state"] != "CLOSED":
                    continue
                title = _prd_number(other["title"])
                if title == nnn or other["number"] in issue["links"] and not title:
                    children.append(other)
            week = now - datetime.timedelta(days=7)
            recent = [c for c in children if _utc(c["closedAt"]) >= week]
            print("solved: %d (%d in the last 7 days)" % (len(children), len(recent)))
            open_children = [o for o in opened if _prd_number(o["title"]) == nnn]
            solvable = 0
            for label in sorted({l["name"] for o in open_children for l in o["labels"]}):
                listed = solvable_issues.solvable(label)[1]
                solvable += sum(1 for o in open_children if o["number"] in listed)
            waiting = [(o["number"], b) for o in open_children
                       for b in o["blockedBy"] if b in open_numbers]
            unheld = sum(1 for o in open_children
                         if not any(l["name"].split(":")[0] == "ready-for-agent" for l in o["labels"])
                         and not issue_worktree.remote_issue_branch("tdd/%d" % o["number"]))
            print("left: solvable now %d, waiting %d on %s, held by no lane %d" % (
                solvable, len({n for n, _ in waiting}),
                ", ".join("#%d" % b for b in sorted({b for _, b in waiting})), unheld))
            if _stale(stored, nnn, issue):
                print("owed: stale")
            else:
                answer = stored[nnn]["answer"]
                print("owed: none" if not answer["count"] else "owed: %d (%s)" % (
                    answer["count"], ", ".join(answer["sections"])))
            lanes = {o["lane"] for o in open_children if o["lane"]}
            if not lanes:
                print("ETA: no lane: no ETA")
                continue
            closed = [o for o in snapshot["issues"] if o["state"] == "CLOSED"
                      and o["lane"] in lanes and _utc(o["closedAt"]) >= week]
            if len(closed) < 3:
                print("ETA: no rate yet")
                continue
            fastest = 0
            slowest = None
            for lane in {o["lane"] for o in closed}:
                walls = sorted(o["wallSeconds"] for o in closed if o["lane"] == lane)
                fastest = max(fastest, 86400 / walls[(len(walls) - 1) // 4])
                rate = 86400 / walls[-1 - (len(walls) - 1) // 4]
                slowest = rate if slowest is None else min(slowest, rate)
            by_number = {o["number"]: o for o in opened}

            def chain(number):
                return 1 + max([chain(b) for b in by_number[number]["blockedBy"] if b in by_number],
                               default=0)

            longest = max([len(open_children)] + [chain(o["number"]) for o in open_children])
            print("ETA: %.2f to %.2f days" % (len(open_children) / fastest, longest / slowest))
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

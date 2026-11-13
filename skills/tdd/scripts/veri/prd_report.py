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


def _ordered_heads(opened):
    return sorted(_heads(opened).items(), key=lambda p: int(p[0]))


def _load(path):
    with open(path) as f:
        return json.load(f)


def _owed():
    return _load(OWED) if os.path.exists(OWED) else {}


def _stale(stored, nnn, issue):
    entry = stored.get(nnn, {})
    return "answer" not in entry or entry.get("updatedAt") != issue["updatedAt"]


def _print_stale():
    snapshot = _load(CACHE)
    stored = _load(OWED)
    opened = [o for o in snapshot["issues"] if o["state"] == "OPEN"]
    for nnn, issue in _ordered_heads(opened):
        if _stale(stored, nnn, issue):
            print(nnn)
    return 0


def _store_owed(prd, path):
    heads = _heads(_load(CACHE)["issues"])
    if prd not in heads:
        print("PRD %s is not in the snapshot" % prd, file=sys.stderr)
        return 2
    stored = _owed()
    stored[prd] = {"updatedAt": heads[prd]["updatedAt"], "answer": _load(path)}
    with open(OWED, "w") as f:
        json.dump(stored, f)
    return 0


def _print_solved(snapshot, nnn, issue, now):
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


def _print_left(nnn, issue, opened, open_children):
    open_numbers = {o["number"] for o in opened}
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


def _print_owed(stored, nnn, issue):
    if _stale(stored, nnn, issue):
        print("owed: stale")
    else:
        answer = stored[nnn]["answer"]
        print("owed: none" if not answer["count"] else "owed: %d (%s)" % (
            answer["count"], ", ".join(answer["sections"])))


def _lane_rates(closed):
    fast_rates = []
    slow_rates = []
    for lane in {o["lane"] for o in closed}:
        walls = sorted(o["wallSeconds"] for o in closed if o["lane"] == lane)
        fast_rates.append(86400 / walls[(len(walls) - 1) // 4])
        slow_rates.append(86400 / walls[-1 - (len(walls) - 1) // 4])
    return max(fast_rates), min(slow_rates)


def _print_eta(snapshot, opened, open_children, now):
    week = now - datetime.timedelta(days=7)
    lanes = {o["lane"] for o in open_children if o["lane"]}
    if not lanes:
        print("ETA: no lane: no ETA")
        return
    closed = [o for o in snapshot["issues"] if o["state"] == "CLOSED"
              and o["lane"] in lanes and _utc(o["closedAt"]) >= week]
    if len(closed) < 3:
        print("ETA: no rate yet")
        return
    fastest, slowest = _lane_rates(closed)
    by_number = {o["number"]: o for o in opened}

    def chain(number):
        return 1 + max([chain(b) for b in by_number[number]["blockedBy"] if b in by_number],
                       default=0)

    longest = max([len(open_children)] + [chain(o["number"]) for o in open_children])
    print("ETA: %.2f to %.2f days" % (len(open_children) / fastest, longest / slowest))


def _print_prd(snapshot, opened, stored, nnn, issue, now):
    print("PRD %s (#%d) — %s" % (nnn, issue["number"], issue["title"]))
    _print_solved(snapshot, nnn, issue, now)
    open_children = [o for o in opened if _prd_number(o["title"]) == nnn]
    _print_left(nnn, issue, opened, open_children)
    _print_owed(stored, nnn, issue)
    _print_eta(snapshot, opened, open_children, now)


def _print_report():
    if not os.path.exists(CACHE):
        print("no snapshot: %s is missing" % CACHE, file=sys.stderr)
        return 2
    snapshot = _load(CACHE)
    now = datetime.datetime.now(datetime.timezone.utc)
    hours = int((now - _utc(snapshot["fetched_at"])).total_seconds() // 3600)
    print("snapshot age: %d hours" % hours)
    opened = [o for o in snapshot["issues"] if o["state"] == "OPEN"]
    stored = _owed()
    for nnn, issue in _ordered_heads(opened):
        _print_prd(snapshot, opened, stored, nnn, issue, now)
    return 0


def main(argv):
    if argv == ["--stale"]:
        return _print_stale()
    if not argv:
        print("usage: report.sh --report | --stale | --store-owed <prd> <file>", file=sys.stderr)
        return 2
    if argv[0] == "--store-owed":
        return _store_owed(argv[1], argv[2])
    if argv == ["--report"]:
        return _print_report()
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

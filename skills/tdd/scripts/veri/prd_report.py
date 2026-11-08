"""report.sh's renderer, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import datetime
import json
import os
import re
import sys

import solvable_issues

USAGE = "usage: report.sh --report"
CACHE = ".tdd/report-cache.json"


def _utc(stamp):
    return datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def main(argv):
    if argv == ["--report"]:
        if not os.path.exists(CACHE):
            print("no snapshot: %s is missing" % CACHE, file=sys.stderr)
            return 2
        with open(CACHE) as f:
            snapshot = json.load(f)
        now = datetime.datetime.now(datetime.timezone.utc)
        hours = int((now - _utc(snapshot["fetched_at"])).total_seconds() // 3600)
        print("snapshot age: %d hours" % hours)
        heads = {}
        for issue in snapshot["issues"]:
            match = re.match(r"PRD (\d+)", issue["title"])
            if match and issue["state"] == "OPEN":
                known = heads.get(match.group(1))
                if known is None or issue["number"] < known["number"]:
                    heads[match.group(1)] = issue
        for nnn, issue in sorted(heads.items(), key=lambda p: int(p[0])):
            print("PRD %s (#%d) — %s" % (nnn, issue["number"], issue["title"]))
            children = []
            for other in snapshot["issues"]:
                if other["state"] != "CLOSED":
                    continue
                title = re.match(r"PRD (\d+)", other["title"])
                if title and title.group(1) == nnn or other["number"] in issue["links"] and not title:
                    children.append(other)
            week = now - datetime.timedelta(days=7)
            recent = [c for c in children if _utc(c["closedAt"]) >= week]
            print("solved: %d (%d in the last 7 days)" % (len(children), len(recent)))
            open_children = [o for o in snapshot["issues"] if o["state"] == "OPEN"
                             and re.match(r"PRD (\d+)", o["title"])
                             and re.match(r"PRD (\d+)", o["title"]).group(1) == nnn]
            solvable = 0
            for label in sorted({l["name"] for o in open_children for l in o["labels"]}):
                listed = solvable_issues.solvable(label)[1]
                solvable += sum(1 for o in open_children if o["number"] in listed)
            print("left: solvable now %d" % solvable)
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

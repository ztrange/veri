"""Usage: serve.py --repo <path> --port <n>"""
import argparse
import datetime
import json
import os
import pathlib
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

ENDING = {"done", "bail", "merged"}


def _minutes(events):
    return (int(events[-1]["awake"]) - int(events[0]["awake"])) // 60


def _unless_empty(items, render):
    return render(items) if items else ""


def _steps(events):
    plans = [e for e in events if e.get("event") == "plan"]
    done = sum(1 for e in events if e.get("event") == "step-done")
    return _unless_empty(plans, lambda p: " %d/%d" % (done, int(p[-1]["steps"])))


def _phase(events):
    launches = [e["phase"] for e in events if e.get("event") == "launch"]
    return _unless_empty(launches, lambda l: " %s attempt %d" % (l[-1], l.count(l[-1])))


def _counts(events):
    verdicts = [e.get("verdict") for e in events if e.get("event") == "verdict"]
    return _unless_empty(verdicts, lambda v: " PASS %d REJECT %d" % (v.count("PASS"), v.count("REJECT")))


def _cost(events):
    usage = [float(e["total_cost_usd"]) for e in events if e.get("event") == "usage"]
    return _unless_empty(usage, lambda u: " | total | $%.2f" % sum(u))


def _split(events):
    models = {}
    for e in events:
        if e.get("model"):
            models[e["name"].split("-")[0]] = e["model"]
    return _unless_empty(models, lambda m: " " + " ".join(
        "%s %s" % (r, m[k]) for k, r in
        (("develop", "developer"), ("verify", "verifier"), ("revise", "revise")) if k in m))


def _run_line(path, events):
    return "<p>%s %dm%s%s%s%s%s</p>" % (
        path.stem, _minutes(events), _steps(events), _phase(events),
        _counts(events), _cost(events), _split(events))


def running_lines():
    lines = []
    runs = pathlib.Path(os.environ["VERI_HOME"]) / "runs"
    for path in sorted(runs.glob("*.jsonl")):
        events = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        if not events or any(e.get("event") in ENDING for e in events):
            continue
        lines.append(_run_line(path, events))
    return lines


SCRIPT = """<script>
setInterval(() => fetch("/running").then(r => r.text()).then(t => {
  document.getElementById("running").innerHTML = t;
}), 2000);
</script>"""


def prd_number(title):
    m = re.match(r"PRD (\d+)", title)
    return int(m.group(1)) if m else None


def report_blocks(repo):
    cache = json.loads((pathlib.Path(repo) / ".tdd" / "report-cache.json").read_text())
    first = {}
    for i in sorted(cache["issues"], key=lambda i: i["number"]):
        n = prd_number(i["title"])
        if n is not None and i["state"] == "OPEN":
            first.setdefault(n, i)
    owed_path = pathlib.Path(repo) / ".tdd" / "report-owed.json"
    owed = json.loads(owed_path.read_text()) if owed_path.exists() else {}

    def owed_line(n, i):
        entry = owed.get("%03d" % n)
        if not (entry and entry.get("updatedAt") == i["updatedAt"]):
            return "\n<p>owed: stale</p>"
        answer = entry["answer"]
        if answer["count"] == 0:
            return "\n<p>owed: none</p>"
        return "\n<p>owed: %d (%s)</p>" % (answer["count"], ", ".join(answer["sections"]))

    def closed_last_week(issues):
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
        return [i for i in issues if datetime.datetime.fromisoformat(i["closedAt"]) >= cutoff]

    def solved_line(n, prd):
        closed = [i for i in cache["issues"] if i["state"] == "CLOSED"
                  and (prd_number(i["title"]) == n or i["number"] in prd.get("links", []))]
        return "\n<p>solved: %d (%d in the last 7 days)</p>" % (len(closed), len(closed_last_week(closed)))

    def open_children(n, prd):
        return [i for i in cache["issues"] if i["state"] == "OPEN"
                and prd_number(i["title"]) == n and i["number"] != prd["number"]]

    def left_line(n, prd):
        open_numbers = {i["number"] for i in cache["issues"] if i["state"] == "OPEN"}
        children = open_children(n, prd)
        names = lambda c: [l["name"] for l in c.get("labels", [])]
        has_lane = lambda c: any(x.startswith("ready-for-agent") for x in names(c))
        blockers = lambda c: [b for b in c.get("blockedBy", []) if b in open_numbers]
        waiting = [c for c in children if blockers(c)]
        solvable = [c for c in children if not blockers(c)
                    and has_lane(c)
                    and not any(x.startswith("taken:") for x in names(c))]
        unheld = [c for c in children if not has_lane(c)]
        on = sorted({b for c in waiting for b in blockers(c)})
        return "\n<p>left: solvable now %d, waiting %d on %s, held by no lane %d</p>" % (
            len(solvable), len(waiting), ", ".join("#%d" % b for b in on), len(unheld))

    def eta_line(n, prd):
        lanes = {i.get("lane") for i in open_children(n, prd)} - {None}
        if lanes:
            closed = closed_last_week(i for i in cache["issues"]
                                      if i["state"] == "CLOSED" and i.get("lane") in lanes)
            if len(closed) < 3:
                return "\n<p>ETA: no rate yet</p>"
            fast, slow = [], []
            for lane in lanes:
                walls = sorted(i["wallSeconds"] for i in closed if i.get("lane") == lane)
                fast.append(86400 / walls[(len(walls) - 1) // 4])
                slow.append(86400 / walls[-1 - (len(walls) - 1) // 4])
            children = open_children(n, prd)
            by_number = {i["number"]: i for i in cache["issues"] if i["state"] == "OPEN"}

            def chain(number):
                return 1 + max([chain(b) for b in by_number[number].get("blockedBy", []) if b in by_number],
                               default=0)

            longest = max([len(children)] + [chain(c["number"]) for c in children])
            return "\n<p>ETA: %.2f to %.2f days</p>" % (len(children) / max(fast), longest / min(slow))
        return "\n<p>ETA: no lane: no ETA</p>"

    return "\n".join("<h2>PRD %d (#%d) \u2014 %s</h2>%s%s%s%s" % (n, i["number"], i["title"], solved_line(n, i), left_line(n, i), eta_line(n, i), owed_line(n, i))
                     for n, i in sorted(first.items()))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/report":
            body = ("<!doctype html><title>veri report</title>\n" + report_blocks(self.server.repo)).encode()
        elif self.path == "/running":
            body = "\n".join(running_lines()).encode()
        else:
            running = "\n".join(running_lines())
            body = ("<!doctype html><title>veri dashboard</title>\n<h2>Running</h2>\n<div id=running>\n"
                    + running + "\n</div>\n" + SCRIPT).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    server.repo = args.repo
    server.serve_forever()


if __name__ == "__main__":
    main()

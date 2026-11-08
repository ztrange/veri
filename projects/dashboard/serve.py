"""Usage: serve.py --repo <path> --port <n>"""
import argparse
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


def report_blocks(repo):
    cache = json.loads((pathlib.Path(repo) / ".tdd" / "report-cache.json").read_text())
    first = {}
    for i in sorted(cache["issues"], key=lambda i: i["number"]):
        m = re.match(r"PRD (\d+)", i["title"])
        if m and i["state"] == "OPEN":
            first.setdefault(int(m.group(1)), i)
    return "\n".join("<h2>PRD %d (#%d) \u2014 %s</h2>" % (n, i["number"], i["title"])
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

"""Usage: serve.py --repo <path> --port <n>"""
import argparse
import json
import os
import pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer

ENDING = {"done", "bail", "merged"}


def _minutes(events):
    return (int(events[-1]["awake"]) - int(events[0]["awake"])) // 60


def _steps(events):
    plans = [e for e in events if e.get("event") == "plan"]
    if not plans:
        return ""
    done = sum(1 for e in events if e.get("event") == "step-done")
    return " %d/%d" % (done, int(plans[-1]["steps"]))


def _phase(events):
    launches = [e["phase"] for e in events if e.get("event") == "launch"]
    if not launches:
        return ""
    return " %s attempt %d" % (launches[-1], launches.count(launches[-1]))


def _counts(events):
    verdicts = [e.get("verdict") for e in events if e.get("event") == "verdict"]
    if not verdicts:
        return ""
    return " PASS %d REJECT %d" % (verdicts.count("PASS"), verdicts.count("REJECT"))


def _cost(events):
    usage = [float(e["total_cost_usd"]) for e in events if e.get("event") == "usage"]
    if not usage:
        return ""
    return " | total | $%.2f" % sum(usage)


def _split(events):
    models = {}
    for e in events:
        if e.get("model"):
            models[e["name"].split("-")[0]] = e["model"]
    if not models:
        return ""
    return " " + " ".join("%s %s" % (r, models[k]) for k, r in
                          (("develop", "developer"), ("verify", "verifier"), ("revise", "revise"))
                          if k in models)


def running_lines():
    lines = []
    runs = pathlib.Path(os.environ["VERI_HOME"]) / "runs"
    for path in sorted(runs.glob("*.jsonl")):
        events = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        if not events or any(e.get("event") in ENDING for e in events):
            continue
        minutes = _minutes(events)
        steps = _steps(events)
        phase = _phase(events)
        counts = _counts(events)
        cost = _cost(events)
        split = _split(events)
        lines.append("<p>%s %dm%s%s%s%s%s</p>" % (path.stem, minutes, steps, phase, counts, cost, split))
    return lines


SCRIPT = """<script>
setInterval(() => fetch("/running").then(r => r.text()).then(t => {
  document.getElementById("running").innerHTML = t;
}), 2000);
</script>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        running = "\n".join(running_lines())
        if self.path == "/running":
            body = running.encode()
        else:
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
    HTTPServer(("127.0.0.1",args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()

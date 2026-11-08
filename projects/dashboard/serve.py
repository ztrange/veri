"""Usage: serve.py --repo <path> --port <n>"""
import argparse
import json
import os
import pathlib
from http.server import BaseHTTPRequestHandler, HTTPServer

ENDING = {"done", "bail", "merged"}


def running_lines():
    lines = []
    runs = pathlib.Path(os.environ["VERI_HOME"]) / "runs"
    for path in sorted(runs.glob("*.jsonl")):
        events = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        if not events or any(e.get("event") in ENDING for e in events):
            continue
        minutes = (int(events[-1]["awake"]) - int(events[0]["awake"])) // 60
        plans = [e for e in events if e.get("event") == "plan"]
        steps = ""
        if plans:
            done = sum(1 for e in events if e.get("event") == "step-done")
            steps = " %d/%d" % (done, int(plans[-1]["steps"]))
        launches = [e["phase"] for e in events if e.get("event") == "launch"]
        phase = ""
        if launches:
            phase = " %s attempt %d" % (launches[-1], launches.count(launches[-1]))
        lines.append("<p>%s %dm%s%s</p>" % (path.stem, minutes, steps, phase))
    return lines


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = ("<!doctype html><title>veri dashboard</title>\n<h2>Running</h2>\n"
                + "\n".join(running_lines())).encode()
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

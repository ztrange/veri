#!/usr/bin/env bash
# dashboard.sh — serve the local web dashboard over this repository's veri runs.
#
# Run from a target repo. Binds 127.0.0.1 only, never another interface: a leaf log holds
# the repo's own code and prompts, so the page must not be reachable from the network.
# The server is stdlib-only python3 — no build step, no npm — and the page it serves is
# the `dashboard.html` sitting beside this script, so a foreign repo gets both through
# the installed symlink.
#
# Usage:   dashboard.sh [port]
#          Serves http://127.0.0.1:<port>/ (default 8765) until interrupted. Ctrl-C
#          (SIGINT) is how it is meant to be stopped, so that is a clean stop and not a
#          failure.
# Exit:    0 served and was interrupted
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

exec python3 - "$HERE/dashboard.html" "${1:-8765}" "$HERE/status.sh" "$HERE/metrics.sh" <<'PY'
import glob
import http.server
import json
import os
import re
import signal
import subprocess
import sys

# SIGINT back to the handler that raises KeyboardInterrupt, explicitly. A non-interactive
# shell starts a background child with SIGINT ignored, `exec` keeps that disposition, and
# python only installs its own handler where it finds SIG_DFL — so a server launched in
# the background (which is how anything but a human at a terminal launches it) would
# otherwise ignore the very signal it is meant to stop on and hang forever.
signal.signal(signal.SIGINT, signal.default_int_handler)

page = open(sys.argv[1], "rb").read()
port = int(sys.argv[2])
status_sh = sys.argv[3]
metrics_sh = sys.argv[4]


# What every reader here does to the script it reads: run it, keep its stdout, and let its
# exit status alone. `check=False` throughout because a non-zero status is an answer and
# not a failure — status.sh exits 3 for "no runs", which is the empty document — and
# stderr is discarded because the page is the only reader and a diagnostic on it would
# only garble the body. `cwd=None` runs it in the server's own working directory, which is
# the target repo dashboard.sh was started from.
def capture(argv, cwd=None):
    done = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, check=False)
    return done.stdout


# The Runs pane is a reader of status.sh, not a second implementation of it: the endpoint
# runs the script and hands back its document verbatim, so no field of it is spelled twice
# and the pane cannot drift as status.sh grows.
def runs_json():
    return capture([status_sh, "--json"])


# The runs the Metrics pane reports on are the ones status.sh reports on, and they are
# discovered the same way: `.tdd/wt/*` under the MAIN working tree, which is git's registry
# first line and never the checkout this was called from (status.sh:16). The server runs in
# the target repo, so that is the question git is asked here.
def main_working_tree():
    out = capture(["git", "worktree", "list", "--porcelain"])
    first = out.decode("utf-8", "replace").splitlines()[:1]
    return first[0][len("worktree "):] if first else ""


# A run has ENDED when its log carries the mark that ends one — `done` or `bail`, the same
# pair status.sh reads for its `state` (status.sh:76). That, and not a clock, is what splits
# the two readings below: a run still going is recomputed, an ended one is quoted.
def run_ended(log):
    ended = False
    with open(log) as f:
        for raw in f:
            raw = raw.strip()
            if raw and json.loads(raw).get("event") in ("done", "bail"):
                ended = True
    return ended


# The Metrics pane, per issue. For a run still going the report is RECOMPUTED by running
# metrics.sh in that run's worktree, the way the conductor calls it, because a run that is
# still spending has a committed report that stopped being true when the step after it
# started. For a run that ended it is `.tdd/issue-<n>-metrics.md` verbatim — the account of
# the run as it was written, which outlives a log that may since have been pruned.
#
# `issue-<digits>.md` rather than `issue-*.md`: the committed report sits in the same
# directory under a name the looser glob also matches, and `31-metrics` is not an issue.
def metrics_json():
    issues = {}
    tree = main_working_tree()
    for run in sorted(glob.glob(os.path.join(tree, ".tdd", "wt", "*"))):
        log = os.path.join(run, ".tdd", "events.jsonl")
        for ledger in sorted(glob.glob(os.path.join(run, ".tdd", "issue-*.md"))):
            found = re.match(r"^issue-([0-9]+)\.md$", os.path.basename(ledger))
            if not found:
                continue
            issue = found.group(1)
            committed = os.path.join(run, ".tdd", "issue-%s-metrics.md" % issue)
            if os.path.exists(log) and run_ended(log):
                issues[issue] = (open(committed).read()
                                 if os.path.exists(committed) else "")
            else:
                issues[issue] = capture([metrics_sh, issue],
                                        cwd=run).decode("utf-8", "replace")
    return json.dumps({"issues": issues}).encode()


# One entry per JSON pane: the path it is polled at, and the reader that answers it. A
# pane is a line here rather than a branch below, so the only thing adding one decides is
# what it serves — that every endpoint is JSON, and how JSON is sent, is settled once.
endpoints = {"/api/runs": runs_json, "/api/metrics": metrics_json}


class Handler(http.server.BaseHTTPRequestHandler):
    # Every 200 this server sends is the same five calls over a different body and type, so
    # they are written once: a pane added later declares what it serves, not how to serve it.
    # Content-Length explicitly because the default is a chunked-less HTTP/1.0 close, and a
    # client then cannot tell a truncated answer from a complete one.
    def respond(self, ctype, body):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.respond("text/html; charset=utf-8", page)
        elif self.path in endpoints:
            self.respond("application/json; charset=utf-8", endpoints[self.path]())
        else:
            self.send_error(404)

    # One line per request on stderr would race the page's polling into a wall of noise,
    # and nothing reads it: the run's own log is events.jsonl.
    def log_message(self, fmt, *args):
        pass


# HTTPServer rather than a bare TCPServer for its SO_REUSEADDR: without it the port is
# unbindable for a minute after the last client's connection closes, so a restart — or a
# second run of the suite — would fail on a port nothing is listening on.
with http.server.HTTPServer(("127.0.0.1", port), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        # SIGINT is the documented way to stop this, so it is exit 0 — not the 130 a
        # process killed by the signal would otherwise report.
        pass
PY

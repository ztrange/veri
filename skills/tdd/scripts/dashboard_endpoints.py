# dashboard_endpoints.py — the server dashboard.sh execs, and its endpoint functions.
# Usage: dashboard_endpoints.py <dashboard.html> <port> <status.sh> <metrics.sh>
import glob
import http.server
import json
import os
import re
import signal
import subprocess
import sys
import urllib.parse

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
def runs_json(query):
    return capture([status_sh, "--json"])


# The runs the Metrics pane reports on are the ones status.sh reports on, and they are
# discovered the same way: `.tdd/wt/*` under the MAIN working tree, which is git's registry
# first line and never the checkout this was called from (status.sh:16). The server runs in
# the target repo, so that is the question git is asked here.
def main_working_tree():
    out = capture(["git", "worktree", "list", "--porcelain"])
    first = out.decode("utf-8", "replace").splitlines()[:1]
    return first[0][len("worktree "):] if first else ""


# One run's event log, parsed, in the order the file has them — a log is appended to, so that
# order is oldest first and newest last. A run that has not logged anything yet, or that has
# no log at all, is the empty list and not an error: both readers below are polled every two
# seconds while a run is still being born. Where the log lives and how a line of it becomes an
# object is settled here, so neither of them spells it.
def events_of(run):
    log = os.path.join(run, ".tdd", "events.jsonl") if run else ""
    if not log or not os.path.exists(log):
        return []
    with open(log) as f:
        return [json.loads(raw) for raw in f if raw.strip()]


# A run has ENDED when its log carries the mark that ends one — `done` or `bail`, the same
# pair status.sh reads for its `state` (status.sh:76). That, and not a clock, is what splits
# the two readings below: a run still going is recomputed, an ended one is quoted.
def run_ended(run):
    return any(e.get("event") in ("done", "bail") for e in events_of(run))


# One issue's report, which is the whole of the split the criterion names. For a run still
# going it is RECOMPUTED by running metrics.sh in that run's worktree, the way the conductor
# calls it, because a run that is still spending has a committed report that stopped being
# true when the step after it started. For a run that ended it is
# `.tdd/issue-<n>-metrics.md` verbatim — the account of the run as it was written, which
# outlives a log that may since have been pruned; a run that ended without one leaves the
# empty string rather than a recomputation of the same log the file was written from.
def issue_report(run, issue):
    committed = os.path.join(run, ".tdd", "issue-%s-metrics.md" % issue)
    if run_ended(run):
        return open(committed).read() if os.path.exists(committed) else ""
    return capture([metrics_sh, issue], cwd=run).decode("utf-8", "replace")


# Every run of this repository, in a stable order: `.tdd/wt/*` under the main working tree,
# which is the set status.sh reports on. Both readers below walk it — one to collect every
# issue, one to find the run holding a named issue's ledger — so where a run lives is spelled
# here and not in either of them.
def runs():
    return sorted(glob.glob(os.path.join(main_working_tree(), ".tdd", "wt", "*")))


# The Metrics pane: every issue every run holds a ledger for, and its report. The walk is
# all this is — which run and which issue, never how one is read.
#
# `issue-<digits>.md` rather than `issue-*.md`: the committed report sits in the same
# directory under a name the looser glob also matches, and `31-metrics` is not an issue.
def metrics_json(query):
    issues = {}
    for run in runs():
        for ledger in sorted(glob.glob(os.path.join(run, ".tdd", "issue-*.md"))):
            found = re.match(r"^issue-([0-9]+)\.md$", os.path.basename(ledger))
            if found:
                issues[found.group(1)] = issue_report(run, found.group(1))
    return json.dumps({"issues": issues}).encode()


# Which run a pane was asked about, by issue number — the name a run goes by everywhere
# else the page reads: status.sh keys each run object by `issue` and the Metrics endpoint
# keys `issues` by the same number. The run is the one holding that issue's ledger, which is
# how metrics_json above already decides which issue a run is for, read the other way round.
def run_for_issue(issue):
    for run in runs():
        if issue and os.path.exists(os.path.join(run, ".tdd", "issue-%s.md" % issue)):
            return run
    return ""


# The Events pane: the selected run's log, oldest first and so newest last — the pane's
# promise is that the order the file has is not reordered. An issue no run holds a ledger for
# is the empty list, which is what events_of makes of the empty run name.
def events_json(query):
    events = events_of(run_for_issue(query.get("issue", [""])[0]))
    return json.dumps({"events": events}).encode()


# One entry per JSON pane: the path it is polled at, and the reader that answers it. A
# pane is a line here rather than a branch below, so the only thing adding one decides is
# what it serves — that every endpoint is JSON, and how JSON is sent, is settled once. Every
# reader takes the request's parsed query string, whether or not it reads anything out of
# it, so that which panes take a parameter stays the readers' business and not the
# dispatcher's.
endpoints = {"/api/runs": runs_json, "/api/metrics": metrics_json,
             "/api/events": events_json}


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

    # The query string is split off before the path is matched: an endpoint is named by its
    # path, and `?issue=41` selects what it answers about rather than naming a second
    # endpoint.
    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path == "/":
            self.respond("text/html; charset=utf-8", page)
        elif path in endpoints:
            self.respond("application/json; charset=utf-8",
                         endpoints[path](urllib.parse.parse_qs(query)))
        else:
            self.send_error(404)

    # One line per request on stderr would race the page's polling into a wall of noise,
    # and nothing reads it: the run's own log is events.jsonl.
    def log_message(self, fmt, *args):
        pass


# ThreadingHTTPServer rather than a plain HTTPServer because HTTPServer answers one request
# at a time: /api/runs shells out to status.sh, which takes tens of seconds on a repo with
# live runs, and every other pane's request queued behind it (#344). A thread per request
# means a slow endpoint cannot starve the cheap ones. It subclasses HTTPServer, so it keeps
# that class's SO_REUSEADDR — without it the port is unbindable for a minute after the last
# client's connection closes, so a restart — or a second run of the suite — would fail on a
# port nothing is listening on — and the bind stays loopback-only. Its threads are daemons,
# so a request still inside status.sh cannot hold the process open past SIGINT.
# Only when run as the program: importing this file to call an endpoint function must not
# bind the port (#330).
if __name__ == "__main__":
    # SIGINT back to the handler that raises KeyboardInterrupt, explicitly. A non-interactive
    # shell starts a background child with SIGINT ignored, `exec` keeps that disposition, and
    # python only installs its own handler where it finds SIG_DFL — so a server launched in
    # the background (which is how anything but a human at a terminal launches it) would
    # otherwise ignore the very signal it is meant to stop on and hang forever. Here and not
    # at import, because a process that imports this to call an endpoint owns its own SIGINT.
    signal.signal(signal.SIGINT, signal.default_int_handler)

    # The page and the port are the server's alone: no endpoint function reads either.
    page = open(sys.argv[1], "rb").read()
    port = int(sys.argv[2])

    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            # SIGINT is the documented way to stop this, so it is exit 0 — not the 130 a
            # process killed by the signal would otherwise report.
            pass

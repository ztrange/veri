"""dashboard.sh's server and its endpoint functions, run in-process."""
import glob
import http.server
import json
import os
import re
import signal
import subprocess
import sys
import urllib.parse

from event_log import read_events
from run_dir import run_file

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
status_sh = os.path.join(SCRIPTS, "status.sh")
metrics_sh = os.path.join(SCRIPTS, "metrics.sh")
# The renderer the Chatter pane shows a leaf log through — the script beside this one, run
# rather than re-implemented, the way runs_json runs status.sh: what "rendered" means is
# render-leaf-log.sh's answer, so the pane cannot drift into a second spelling of it. It
# reads the log on stdin and writes the rendered lines out; a log it cannot render (exit 2
# on a line that is not JSON) leaves NOTHING, not what it managed, because it writes its
# accumulated output only after the loop that exit leaves (render-leaf-log.sh:33-46).
render_leaf_log_sh = os.path.join(SCRIPTS, "render-leaf-log.sh")


# What every reader here does to the script it reads: run it, keep its stdout, and let its
# exit status alone. `check=False` throughout because a non-zero status is an answer and
# not a failure — status.sh exits 3 for "no runs", which is the empty document — and
# stderr is discarded because the page is the only reader and a diagnostic on it would
# only garble the body. `cwd=None` runs it in the server's own working directory, which is
# the target repo dashboard.sh was started from, and `feed=None` leaves the child the server's
# own stdin — a reader with bytes for the script to read on stdin hands them over instead.
def capture(argv, cwd=None, feed=None):
    done = subprocess.run(argv, cwd=cwd, input=feed, stdout=subprocess.PIPE,
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


# Where one run's event log lives, or nothing when the run has none — the path, asked before
# it is read, because whether a run HAS a log is a fact of its own and not only a step on the
# way to its lines. A run that has one is a run whose every step was recorded, so its log is
# the whole account of what it did; a run with none recorded nothing, and nothing about it can
# be read out of marks it never wrote.
def event_log(run):
    log = run_file(run, "events.jsonl") if run else ""
    return log if log and os.path.exists(log) else ""


# One run's event log, parsed, in the order the file has them — a log is appended to, so that
# order is oldest first and newest last. A run that has not logged anything yet, or that has
# no log at all, is the empty list and not an error: both readers below are polled every two
# seconds while a run is still being born. Where the log lives and how a line of it becomes an
# object is settled here, so neither of them spells it.
def events_of(run):
    log = event_log(run)
    if not log:
        return []
    return read_events(log)


# The lines of one run's log carrying one of the marks named — which field of a line says
# which mark it is, asked here and not by each reader that wants a kind of mark. Both of
# them below read a mark this way: the one that decides a run has ended, and the one the
# Tests pane counts.
def events_marked(run, *marks):
    return [event for event in events_of(run) if event.get("event") in marks]


# A run has ENDED when its log carries the mark that ends one — `done` or `bail`, the same
# pair status.sh reads for its `state` (status.sh:76). That, and not a clock, is what splits
# the two readings below: a run still going is recomputed, an ended one is quoted.
def run_ended(run):
    return bool(events_marked(run, "done", "bail"))


# One issue's report, which is the whole of the split the criterion names. For a run still
# going it is RECOMPUTED by running metrics.sh in that run's worktree, the way the conductor
# calls it, because a run that is still spending has a committed report that stopped being
# true when the step after it started. For a run that ended it is
# `.tdd/issue-<n>-metrics.md` verbatim — the account of the run as it was written, which
# outlives a log that may since have been pruned.
#
# A run that ended without one is not recomputed either: the log the file would be written
# from is the same one, and the missing file is the thing worth saying. It used to leave the
# empty string, which reads on the page as "this run had nothing to report" rather than "the
# report is missing" (#295). So it leaves a MARKER naming the file that is not there — the
# only thing a viewer can tell apart from a real empty report.
def issue_report(run, issue):
    # The report's path under the run, spelled once: the file that is read when it is there
    # and the file the marker names when it is not are the same one, and two spellings of it
    # would let the marker name a path the reader never looked at.
    report = os.path.join(".tdd", "issue-%s-metrics.md" % issue)
    committed = os.path.join(run, report)
    if run_ended(run):
        if os.path.exists(committed):
            return open(committed).read()
        return "(no report: this run ended without committing %s)" % report
    return capture([metrics_sh, issue], cwd=run).decode("utf-8", "replace")


# Every run of this repository, in a stable order: `.tdd/wt/*` under the main working tree,
# which is the set status.sh reports on. Both readers below walk it — one to collect every
# issue, one to find the run holding a named issue's ledger — so where a run lives is spelled
# here and not in either of them.
def runs():
    return sorted(glob.glob(os.path.join(main_working_tree(), ".tdd", "wt", "*")))


# Whether a run holds issue `<n>`'s ledger — the one question both readers below ask of a run,
# so where a ledger lives is spelled here and not in either of them. An empty issue holds
# nothing: the Events pane is polled with no issue selected, and the name of a run directory
# that is not a number is no issue at all.
def has_ledger(run, issue):
    return bool(issue) and os.path.exists(
        run_file(run, "issue-%s.md" % issue))


# The Metrics pane: one entry per run directory, and its report. The walk is all this is —
# which run and which issue, never how one is read.
#
# The issue a run is for is its directory's own name — `.tdd/wt/7` is issue 7 — and not
# whichever ledgers it holds: ledgers are committed, so every run worktree carries a copy of
# every earlier issue's plan, and globbing them reported one entry per copy and ran
# metrics.sh once for each (#343). A directory whose own `issue-<n>.md` is not there yet is
# a run still being born and contributes nothing.
def run_issue(run):
    found = re.match(r"^([0-9]+)$", os.path.basename(run))
    return found.group(1) if found else ""


def metrics_json(query):
    issues = {}
    for run in runs():
        issue = run_issue(run)
        if has_ledger(run, issue):
            issues[issue] = issue_report(run, issue)
    return json.dumps({"issues": issues}).encode()


# Which run a pane was asked about, by issue number — the name a run goes by everywhere
# else the page reads: status.sh keys each run object by `issue` and the Metrics endpoint
# keys `issues` by the same number. The run is `.tdd/wt/<issue>` and no other, which is how
# metrics_json above already decides which issue a run is for, read the other way round:
# holding `issue-<n>.md` does not make a run issue `<n>`'s, because ledgers are committed and
# every run worktree carries a copy of every earlier issue's plan (#343). An issue with no run
# directory of its own is no run, and its pane is the empty log rather than another run's.
def run_for_issue(issue):
    for run in runs():
        if run_issue(run) == issue and has_ledger(run, issue):
            return run
    return ""


# Which issue a request selected: the `issue=` of its parsed query string, or the empty name
# when it carries none — a pane is polled with nothing selected before the reader picks a run.
# Every pane that answers about one run asks this, so how a request names its run is read out
# of the query string here and not once per endpoint.
def selected_issue(query):
    return query.get("issue", [""])[0]


# The Events pane: the selected run's log, oldest first and so newest last — the pane's
# promise is that the order the file has is not reordered. An issue no run holds a ledger for
# is the empty list, which is what events_of makes of the empty run name.
def events_json(query):
    events = events_of(run_for_issue(selected_issue(query)))
    return json.dumps({"events": events}).encode()


# The command the run's leaves were told to run — the `Test command:` line of the run's own
# spec file, which is where the conductor recorded it for this issue (SKILL.md:508). Read here
# rather than detected afresh, because what the Tests pane reports is the runs the leaves
# performed, and a leaf ran the command the spec named; a run whose spec names none has no
# test command, and so no test run to list.
TEST_COMMAND = "Test command:"


def test_command(run, issue):
    spec = run_file(run, "issue-%s-spec.md" % issue) if run else ""
    if not spec or not os.path.exists(spec):
        return ""
    with open(spec) as f:
        for line in f:
            _, marker, rest = line.partition(TEST_COMMAND)
            if marker and rest.strip():
                return rest.strip()
    return ""


# The tail of one test run's output: its last few lines, which is where a suite in this house
# puts what a reader wants — the count line it ends with, and the FAIL lines just above it.
# A whole `make test` output is thousands of lines and the pane shows one entry per run, so
# what is cut is the part no one reads.
TAIL_LINES = 10


def output_tail(text):
    return "\n".join(text.splitlines()[-TAIL_LINES:])


# Where one leaf's transcript lives. `.tdd/<leaf>.log` is supervise.sh's own capture of the
# leaf's combined output (supervise.sh:211), and supervise.sh is the choke point EVERY leaf
# goes through; `.tdd/<leaf>.out` is a shell redirection the conductor types on a developer
# leaf's launch line alone (SKILL.md:617), so a verifier — launched through verify.sh, whose
# outer redirect goes to /dev/null (SKILL.md:307) — never gets one. Where both exist they are
# the same bytes, so the log every leaf writes is what is read, and the redirection only where
# a run wrote no `.log` beside it (#384). No run, or no leaf, names no log. The two suffixes
# are named here rather than spelled at each use, because leaf_logs below has to glob for the
# same one this falls back to and a second spelling of it would be a set of logs that disagreed
# with the log.
SUPERVISED_LOG = ".log"
CONDUCTOR_OUT = ".out"


def leaf_log(run, leaf):
    if not run or not leaf:
        return ""
    supervised = run_file(run, leaf + SUPERVISED_LOG)
    if os.path.exists(supervised):
        return supervised
    return run_file(run, leaf + CONDUCTOR_OUT)


# Every leaf log of one run, in a stable order — the whole set, as the glob of any leaf name.
# Spelled here rather than through leaf_log above, because that one answers about a named leaf
# and so decides between the two spellings by asking whether the file is there, which no glob
# pattern can be. A run still being born has none, which is the empty list and not an error,
# and so is the empty run name.
def leaf_logs(run):
    return sorted(glob.glob(run_file(run, "*" + CONDUCTOR_OUT))) if run else []


# One leaf log's records: its stream-json lines, parsed, one per line and in the order the
# file has them. A line that is not JSON is skipped rather than raised on, because this reads
# a log the leaf may still be writing — the last line of a live one is routinely half a
# record — and a pane that died on it would go blank for as long as the write took. That is
# the difference from events_of above, which reads a log written a whole line at a time.
def log_records(log):
    with open(log) as f:
        for raw in f:
            if not raw.strip():
                continue
            try:
                yield json.loads(raw)
            except ValueError:
                continue


# The test runs a run's LEAF LOGS account for, read back out of their records — the
# dashboard runs no suite itself, and could not: a suite takes minutes and would run again on
# every poll. A test run is a Bash tool call whose command is the run's own test command,
# paired with the tool result carrying its answer; the pairing is by `tool_use_id`, because a
# leaf's call and its result are separate records and other calls sit between them. A Bash
# call to anything else is no run of the suite, and so is not listed.
def logged_test_runs(run, command):
    found = []
    for log in leaf_logs(run):
        pending = set()
        for obj in log_records(log):
            for block in (obj.get("message") or {}).get("content") or []:
                if (block.get("type") == "tool_use" and block.get("name") == "Bash"
                        and (block.get("input") or {}).get("command") == command):
                    pending.add(block.get("id"))
                elif (block.get("type") == "tool_result"
                        and block.get("tool_use_id") in pending):
                    pending.discard(block.get("tool_use_id"))
                    found.append({
                        "command": command,
                        "passed": not block.get("is_error", False),
                        "tail": output_tail(str(block.get("content", ""))),
                    })
    return found


# The same test runs, read out of the run's own event log rather than its leaf logs: one entry
# per `test-run` mark, the line timed-test-run.sh:45 appends per test-command run since #342 —
# when a leaf stopped typing its test command as a bare Bash call and started invoking the
# wrapper by absolute path instead (#383). That is why the mark and not the leaf log is what
# the pane counts today: logged_test_runs' string match against the spec's command could
# never hold again, and the pane went empty on a live run that had already run its suite
# seven times.
#
# Each entry says which suites that run covered and whether it came back green, both read off
# the mark itself: `suites` is the list timed-test-run.sh was handed (empty for a whole-suite
# tier, which covers them all and names none), and `status` is the test command's own exit
# status, so a run passed when that status was success. The command is the spec's, the one
# logged_test_runs above names too, because the mark does not carry it.
def marked_test_runs(run, command):
    return [{"command": command,
             "suites": mark.get("suites", ""),
             "passed": mark.get("status") == "0"}
            for mark in events_marked(run, "test-run")]


# Answered for the selected run alone, the way every endpoint has since #343: the run is
# `.tdd/wt/<issue>` and no other, so a second run whose leaves ran the same command is not
# reported here. An issue with no run of its own, or one whose spec names no test command,
# is the empty list rather than another run's tests. The issue the spec is read for is the
# one that was asked about: run_for_issue answers with `.tdd/wt/<issue>` and no other, so
# asking the run back for its own number could only return the number already in hand.
def tests_json(query):
    issue = selected_issue(query)
    run = run_for_issue(issue)
    command = test_command(run, issue)
    # A run that HAS an event log is answered out of that log alone, by marked_test_runs
    # above: every test-command run it performed appended a `test-run` mark there, so a log
    # carrying none is a run that ran the suite no times — the empty list. That the marks are
    # read for the selected run's log and no other is what keeps a run beside it, whose leaves
    # ran the same command, out of the answer.
    #
    # A run with NO event log recorded nothing, and its leaf logs are the only account of it
    # there is: that is the one case still read the old way, and the only thing a run predating
    # the mark has to be read out of. Which of the two answers is a fact about the run and not
    # a choice made here.
    if event_log(run):
        tests = marked_test_runs(run, command)
    else:
        tests = logged_test_runs(run, command) if command else []
    return json.dumps({"tests": tests}).encode()


# So what the renderer is handed is the log's stream-json records alone, and not the blank
# line and plain-text result run-leaf.sh appends after them once the leaf closes
# (run-leaf.sh:82-83). Handed the whole file, the renderer refuses on that tail and throws
# away every record it had already rendered, so the pane went blank the moment a leaf
# finished — developer leaves included (#384). The tail is dropped here rather than tolerated
# there because "a line that is not JSON is no answer the renderer can give" is the renderer's
# own contract (render-leaf-log.sh:11), and it is the caller holding a log of two parts that
# knows which part is a transcript.
def record_lines(log):
    kept = []
    with open(log, "rb") as f:
        for raw in f:
            try:
                json.loads(raw)
            except ValueError:
                continue
            kept.append(raw)
    return b"".join(kept)


def rendered_log(log):
    if not log or not os.path.exists(log):
        return ""
    return capture([render_leaf_log_sh],
                   feed=record_lines(log)).decode("utf-8", "replace")


# The leaf a run is CURRENTLY on: the name its newest `launch` event carries, which is the
# leaf status.sh reports a run as being on (status.sh:79). The log is appended to, so the
# newest launch is the last one in it — a run that has launched nothing yet is on no leaf.
def current_leaf(run):
    for event in reversed(events_of(run)):
        if event.get("event") == "launch" and event.get("name"):
            return event["name"]
    return ""


# The Chatter pane: the current leaf's log, rendered. Answered for the selected run alone,
# like every endpoint since #343. An issue with no run of its own, or a run on no leaf, or a
# leaf that has written nothing yet, is the empty rendering rather than another leaf's.
def chatter_json(query):
    run = run_for_issue(selected_issue(query))
    log = leaf_log(run, current_leaf(run))
    return json.dumps({"chatter": rendered_log(log)}).encode()


# One entry per JSON pane: the path it is polled at, and the reader that answers it. A
# pane is a line here rather than a branch below, so the only thing adding one decides is
# what it serves — that every endpoint is JSON, and how JSON is sent, is settled once. Every
# reader takes the request's parsed query string, whether or not it reads anything out of
# it, so that which panes take a parameter stays the readers' business and not the
# dispatcher's.
endpoints = {"/api/runs": runs_json, "/api/metrics": metrics_json,
             "/api/events": events_json, "/api/tests": tests_json,
             "/api/chatter": chatter_json}


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
def main(argv):
    # SIGINT back to the handler that raises KeyboardInterrupt, explicitly. A non-interactive
    # shell starts a background child with SIGINT ignored, `exec` keeps that disposition, and
    # python only installs its own handler where it finds SIG_DFL — so a server launched in
    # the background (which is how anything but a human at a terminal launches it) would
    # otherwise ignore the very signal it is meant to stop on and hang forever. Here and not
    # at import, because a process that imports this to call an endpoint owns its own SIGINT.
    signal.signal(signal.SIGINT, signal.default_int_handler)

    # The page and the port are the server's alone: no endpoint function reads either.
    global page
    with open(os.path.join(SCRIPTS, "dashboard.html"), "rb") as f:
        page = f.read()
    port = int(argv[0] if argv and argv[0] else "8765")

    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            # SIGINT is the documented way to stop this, so it is exit 0 — not the 130 a
            # process killed by the signal would otherwise report.
            pass
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])

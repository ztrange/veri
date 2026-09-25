#!/usr/bin/env bash
# Unit tests for scripts/dashboard.sh — the local web dashboard over the same run data
# status.sh and metrics.sh read. Run from a target repo, it starts a stdlib-only Python
# server on 127.0.0.1 that serves one static HTML page and a JSON endpoint per pane.
# Zero-dependency plain-shell asserts, same idiom as status.test.sh.
#
# Contract under test (issue #110), this suite's first case:
#   dashboard.sh            with no argument, bind port 8765 and serve the one HTML page
#                           at /; exit 0 when sent SIGINT.
#   dashboard.sh <port>     bind the port named on the command line, and bind it on
#                           127.0.0.1 only — never on another interface.
#   GET /api/runs           return what `status.sh --json` returns, for the repository the
#                           server was started from.
#   GET /api/metrics        return the per-issue report: recomputed from the event log for a
#                           run still going, and the committed `.tdd/issue-<n>-metrics.md`
#                           verbatim for one that ended.
#   GET /api/events?issue=<n>
#                           return that run's `.tdd/events.jsonl` tail, parsed, newest last.
#
# The server is the one script here that cannot be asked a question and answered in the
# same process: it runs until it is told to stop. So the case launches it in the
# background, polls the port until the page answers, and only then interrupts it — the
# same shape status.test.sh's `--watch` case uses for the other long-running script.
#
# Run: scripts/tests/dashboard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DASH="$HERE/../dashboard.sh"
STATUS="$HERE/../status.sh"
METRICS="$HERE/../metrics.sh"
scripts="$(cd "$HERE/.." && pwd)"

# The server's python module, found the way anyone reading dashboard.sh would find it — the
# `.py` beside it that its `exec python3` line names — so no case cares what it is called.
# Found once here for every case that imports it; $module_problem is why it could not be, or
# nothing, and each of those cases fails on it rather than on a module it never loaded.
exec_line="$(grep -E '^exec python3 ' "$DASH" || :)"
module="$(sed -nE 's/^exec python3 .*"\$HERE\/([A-Za-z_][A-Za-z0-9_]*)\.py".*/\1/p' <<< "$exec_line")"
module_problem=""
[[ -n "$module" ]] ||
  module_problem="dashboard.sh execs no .py module beside it; its exec line is: $(printf '%q' "$exec_line")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# Every server this suite starts, counted (#330): a `python3` first on PATH for the whole
# suite that appends one line to $starts whenever it is handed a .py file beside dashboard.sh
# as its script — which is what `dashboard.sh` execs to serve, and nothing else here does —
# then execs the real interpreter with the same arguments. Counted at the exec rather than by
# timing anything, so the last case can ask how many starts there were, not how long they
# took. `#!/bin/sh` like every stub here (#322): it runs once per python3 the suite spawns.
starts="$work/server-starts.log"
: > "$starts"
mkdir -p "$work/shim"
cat > "$work/shim/python3" <<EOF
#!/bin/sh
case "\$1" in
  '$scripts'/*.py) printf '%s\n' "\$*" >> '$starts' ;;
esac
exec '$(command -v python3)' "\$@"
EOF
chmod +x "$work/shim/python3"
export PATH="$work/shim:$PATH"

# The default port the criterion names. Spelled once, because both the URL the case fetches
# and the "is anything already there?" probe below have to mean the same number: a case that
# fetched one port and checked another for squatters could pass against a stranger's server.
PORT=8765

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that it did. Same
# helper as claude-md-counts.test.sh's.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# add_problems — one problem per non-empty line of stdin. Every case that hands its assertions
# to a python3 program reads what that program printed this way: the program says nothing when
# the case passes, and one line per thing that broke when it does not.
add_problems() {
  local line
  while IFS= read -r line; do
    [[ -n "$line" ]] && problems+=("$line")
  done
}

# ask_page <program> [<arg>…] — run a python3 program over the dashboard.html beside
# dashboard.sh and file what it prints as this case's problems, or file the missing page as the
# one problem when there is nothing there to read. Every case that reads the page off disk reads
# it this way; what differs between them is only what their program looks for once it has it.
# The page is the program's argv[1] and any further arguments follow it, which is how one
# program serves several cases that differ only in what they name.
ask_page() {
  local program="$1"
  shift
  if [[ ! -f "$disk_page" ]]; then
    problems+=("there is no dashboard.html beside dashboard.sh to read")
  else
    add_problems < <(python3 -c "$program" "$disk_page" "$@")
  fi
}

# fetches_endpoints <pane>=<path>… — file a problem for every named pane whose endpoint the
# page never fetches. Two cases ask this, of different panes and of nothing else, so what they
# ask lives here once and takes the panes it is asked about as arguments.
fetches_endpoints() {
  ask_page '
import re
import sys

with open(sys.argv[1]) as f:
    page = f.read()

# One endpoint per pane. The path is asked for inside a fetch of a literal, not anywhere on
# the page: the endpoint named in a comment, or in the prose of a heading, is not a poll.
# Matched as a prefix of the literal so that a pane may carry a ?issue= query of its own on
# the end of its path.
for arg in sys.argv[2:]:
    pane, path = arg.split("=", 1)
    if not re.search(r"fetch\s*\(\s*[\"\x27\x60][^\"\x27\x60]*" + re.escape(path), page):
        print("the page never fetches %s, so the %s pane has no endpoint of its own to poll"
              % (path, pane))
' "$@"
}

# A repository of the case's own, so the dashboard is started from a target repo rather than
# from whichever repository `make test` was typed in. A `git init` with no commit is enough,
# exactly as status.test.sh's `repo` helper makes one.
repo() {  # repo <name> -> path
  local dir="$work/$1"
  git init -q -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

# A fabricated run, not a real worktree: .tdd/wt/<n> under <repo> is a repository of its own
# whose unborn branch is the issue branch, with an empty .tdd/ for the ledger and event log.
# Same helper as status.test.sh's, because a run is what status.sh reads and what the endpoint
# under test has to answer with.
fabricate_run() {  # fabricate_run <repo> <n> <branch> -> path
  local dir="$1/.tdd/wt/$2"
  git init -q -b "$3" "$dir" >/dev/null 2>&1
  mkdir -p "$dir/.tdd"
  echo "$dir"
}

# reachable <host> <port> — true when something accepts a connection at that address. Both
# questions this suite asks of a socket are this one. Of another host it asks the second half
# of the criterion: a server bound to 0.0.0.0 answers on this machine's LAN address as
# readily as on 127.0.0.1, and one bound to 127.0.0.1 refuses there, so asking it of the
# loopback alone could never tell the two apart. Of the loopback BEFORE a launch it fails the
# case closed: with a stranger's server on the port, the fetch below would succeed without
# dashboard.sh having bound anything, and a case that cannot tell the two apart must not
# report a pass.
reachable() {  # reachable <host> <port>
  python3 -c 'import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex((sys.argv[1], int(sys.argv[2]))) == 0 else 1)' "$1" "$2"
}

# other_addr — one IPv4 address of this machine that is NOT loopback, or nothing. The UDP
# "connect" sends no packet: it only asks the routing table which local address would be used
# to reach a documentation-range address (RFC 5737, never routed anywhere), which is how a
# host's own address is had without a name server or a live network. `gethostname` is the
# fallback for a machine with no default route.
other_addr() {
  python3 -c 'import socket
found = set()
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("192.0.2.1", 9)); found.add(s.getsockname()[0]); s.close()
except Exception:
    pass
try:
    for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
        found.add(info[4][0])
except Exception:
    pass
for a in sorted(x for x in found if not x.startswith("127.")):
    print(a); break'
}

# free_port — a port the kernel says is free right now: bind 0, read back what it chose,
# close. A hard-coded second port would collide with whatever else this machine is running,
# and the case would then blame dashboard.sh for a stranger. The `reachable` probe below is
# still asked, because "free a moment ago" and "free now" are not the same claim.
free_port() {
  python3 -c 'import socket
s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()'
}

# fetch <url> — GET it with python3, printing the status code on the first line, the
# Content-Type on the second and the body after that; non-zero exit when no answer could be
# had at all, which is what the poll below reads as "not up yet". python3 rather than curl
# because the suites here already lean on python3 (status.test.sh, metrics.test.sh) and on
# nothing else, and an HTTP server that ships as stdlib is fair to question with the stdlib
# client that comes with it.
fetch() {  # fetch <url>
  python3 -c 'import sys, urllib.request, urllib.error
try:
    with urllib.request.urlopen(sys.argv[1], timeout=2) as r:
        print(r.status); print(r.headers.get("Content-Type", ""))
        sys.stdout.write(r.read().decode("utf-8", "replace"))
except urllib.error.HTTPError as e:
    print(e.code); print(e.headers.get("Content-Type", ""))
    sys.stdout.write(e.read().decode("utf-8", "replace"))
except Exception as e:
    print(e, file=sys.stderr); sys.exit(1)' "$1"
}

# The three parts of what `fetch` printed, read back by name. Which line carries the status
# and which the Content-Type is the envelope `fetch` above writes, so it is known here beside
# it rather than in every case that reads one: a case asks for the status, not for line 1.
http_status() { sed -n 1p <<< "$1"; }
http_ctype()  { sed -n 2p <<< "$1"; }
http_body()   { sed -n '3,$p' <<< "$1"; }

# answer_problem <url> <log> <answer> — why <answer> is not this server's 200, or nothing.
# The two ways a fetch can fail before a case has a body to assert on are the same in every
# case here: nothing ever answered, and something answered with the wrong status. The
# server's own output is quoted for the first, because a server that died has said why on
# <log> and nothing else will.
answer_problem() {  # answer_problem <url> <log> <answer>
  local url="$1" log="$2" answer="$3" status
  if [[ -z "$answer" ]]; then
    echo "no answer from $url after 10 s; the server left: $(printf '%q' "$(cat "$log" 2>/dev/null)")"
    return
  fi
  status="$(http_status "$answer")"
  [[ "$status" == 200 ]] || echo "GET $url answered $status, want 200"
}

# serve_until_up <url> — poll <url> until it answers, up to 10 s, and print what `fetch`
# returned; print nothing at all when it never answered, which is what a case reads as "the
# server never came up". Ten seconds is generous because a cold python3 start is the slowest
# thing here, and a poll that gave up early would report "no page" for a server that was
# merely still starting.
serve_until_up() {  # serve_until_up <url>
  local page i=0
  while [[ "$i" -lt 100 ]]; do
    if page="$(fetch "$1" 2>/dev/null)"; then
      printf '%s' "$page"
      return
    fi
    sleep 0.1
    i=$((i + 1))
  done
}

# launch <dash> <repo> <log> [port] — start <dash> in the background from <repo>, its output
# on <log>, and leave its pid in `$!` for the caller to interrupt and wait on. Which
# dashboard.sh is the caller's because the script reads the status.sh sitting beside itself,
# so the concurrency case starts the copy in a directory whose status.sh is its stub while
# every other case starts $DASH; everything else about the start is the same in all of them
# and so is spelled here. `exec` inside the subshell so that pid is the server's own and not
# a shell wrapping it — the SIGINT has to reach the thing that is serving. PYTHONPATH cleared
# and PYTHONNOUSERSITE set so an importable package in the caller's environment cannot be
# what makes it work: "stdlib-only" is part of the criterion, and a server that needed a
# third-party module would have it to hand otherwise. Started here rather than in a command
# substitution because a pid the calling shell is not the parent of cannot be `wait`ed on,
# and the exit status after SIGINT is half of what the first case asks.
launch() {  # launch <dash> <repo> <log> [port]
  local dash="$1" dir="$2" out="$3"
  shift 3
  (cd "$dir" && PYTHONPATH= PYTHONNOUSERSITE=1 exec "$dash" "$@" >"$out" 2>&1) &
}

# port_problem <port> — the reason this case cannot be asked of that port, or nothing. Every
# case here has the same two: the kernel had none to give, and somebody else is already on the
# one it did. Both fail the case closed rather than skipping it, because a fetch answered by a
# stranger's server looks exactly like a fetch answered by dashboard.sh.
port_problem() {  # port_problem <port>
  if [[ -z "$1" ]]; then
    echo "could not get a free port from the kernel, so there was nothing to pass dashboard.sh"
  elif reachable 127.0.0.1 "$1"; then
    echo "port $1 was already in use before dashboard.sh was started, so nothing this case fetches would be its answer"
  fi
}

# stop <pid> — interrupt a launched server and reap it, returning the status it exited
# with. SIGINT rather than SIGTERM because that is the stop the script documents, and the
# status is returned rather than swallowed because for the first case it IS half the
# criterion: a server killed by the signal it is meant to shut down on comes back 130.
# Both `kill` and `wait` are quiet: a server that already died has no pid to signal, and the
# case's own probes are what should say so, not a stray shell message.
stop() {  # stop <pid>
  kill -INT "$1" 2>/dev/null
  wait "$1" 2>/dev/null
}

# call_endpoint <repo> <fn> <err> <query> <out> [<query> <out> …] — import the module in
# <repo>, with the argv dashboard.sh hands it when started with no port argument, and call its
# endpoint function <fn> once per <query> — the parsed query string as JSON, `?issue=41` being
# {"issue": ["41"]} — leaving each answer's bytes on the <out> after it and python's stderr on
# <err>. One python3 process however many calls, and no socket: this is how the payload cases
# ask an endpoint a question without a server. An <out> that was never written is the case's
# sign the call raised, and <err> says why.
call_endpoint() {  # call_endpoint <repo> <fn> <err> <query> <out> [<query> <out> …]
  local dir="$1" fn="$2" err="$3"
  shift 3
  (cd "$dir" && PYTHONPATH= PYTHONNOUSERSITE=1 python3 -c '
import importlib, json, sys

scripts, module, port, fn = sys.argv[1:5]
calls = sys.argv[5:]
sys.path.insert(0, scripts)
sys.argv = [scripts + "/" + module + ".py", scripts + "/dashboard.html", port,
            scripts + "/status.sh", scripts + "/metrics.sh"]
endpoint = getattr(importlib.import_module(module), fn)
for query, out in zip(calls[0::2], calls[1::2]):
    body = endpoint(json.loads(query))
    with open(out, "wb") as f:
        f.write(body)
' "$scripts" "$module" "$PORT" "$fn" "$@") 2> "$err"
}

# The half of an events case that is the same in both of them: two answers call_endpoint
# wrote, each loaded and checked to be an object with an "events" array, and the run log
# they are answers about, parsed the way events_json parses it. Handed
# <body> <issue> <body> <issue> <log>, it leaves `answers` keyed by issue number and `want`
# the log's lines, and says which half of a malformed answer broke rather than dying on it.
# What differs between the two cases is only what they compare those to — the program each
# appends to this one — so the shape check and the log read are written here once.
events_answers='
import json, sys

answers = {}
for path, issue in ((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4])):
    try:
        with open(path) as f:
            got = json.load(f)
    except ValueError:
        with open(path) as f:
            print("events_json for issue %s returned something that is not JSON; it starts: %r"
                  % (issue, f.read()[:200]))
        sys.exit()
    if not isinstance(got, dict) or not isinstance(got.get("events"), list):
        print("events_json for issue %s returned %s; want an object with an \"events\" array"
              % (issue, json.dumps(got, sort_keys=True)[:300]))
        sys.exit()
    answers[issue] = got["events"]
with open(sys.argv[5]) as f:
    want = [json.loads(raw) for raw in f if raw.strip()]
'

# The half of a metrics payload case that is the same in all three of them: the answer
# call_endpoint wrote, loaded and checked to be an object with an "issues" object keyed by the
# runs the fixture made. Handed <body> <issue>[,<issue>…] and whatever else the case names
# after them, it leaves `issues` keyed by issue number, and says which half of a malformed
# answer broke rather than dying on it. What differs between the three cases is only what they
# compare those reports to — the program each appends to this one — so the shape check and the
# roster check are written here once.
metrics_issues='
import json, sys

body, want_issues = sys.argv[1], sys.argv[2].split(",")
try:
    with open(body) as f:
        got = json.load(f)
except ValueError:
    with open(body) as f:
        print("metrics_json returned something that is not JSON; it starts: %r" % f.read()[:200])
    sys.exit()
if not isinstance(got, dict) or not isinstance(got.get("issues"), dict):
    print("metrics_json returned %s; want an object with an \"issues\" object keyed by "
          "issue number" % json.dumps(got, sort_keys=True)[:300])
    sys.exit()
issues = got["issues"]
if sorted(issues) != sorted(want_issues):
    print("metrics_json reports issues %s; want the runs %s"
          % (json.dumps(sorted(issues)), json.dumps(sorted(want_issues))))
    sys.exit()
'

# The half of a Tests case that is the same in all three of them: the answer call_endpoint
# wrote, loaded and checked to be an object with a "tests" array. Handed <body> <issue> and
# whatever else the case names after them, it leaves `runs` that array and `got` the whole
# answer, and says which half of a malformed one broke rather than dying on it. What differs
# between the three cases is only what they compare those runs to — the program each appends
# to this one — so the shape check is written here once.
tests_runs='
import json, sys

body, issue = sys.argv[1], sys.argv[2]
try:
    with open(body) as f:
        got = json.load(f)
except ValueError:
    with open(body) as f:
        print("tests_json for issue %s returned something that is not JSON; it starts: %r"
              % (issue, f.read()[:200]))
    sys.exit()
if not isinstance(got, dict) or not isinstance(got.get("tests"), list):
    print("tests_json for issue %s returned %s; want an object with a \"tests\" array"
          % (issue, json.dumps(got, sort_keys=True)[:300]))
    sys.exit()
runs = got["tests"]
'

# The half of a Chatter case that is the same in all three of them: reading one answer
# call_endpoint wrote. `chatter(<body>, <issue>)` loads it, checks it is an object with a
# "chatter" key, takes the rendering as the renderer’s own text or as the lines of it, and
# hands it back with its surrounding blank lines off — or says which half of a malformed
# answer broke, and hands back None, rather than dying on it. `want(<path>)` reads
# render-leaf-log.sh’s own rendering the same way, so the two sides of every comparison below
# are stripped alike. The third argument names WHICH answer, for the one case that asks twice
# over one run; the two that ask once leave it off. What differs between the cases is only
# what they say when the two sides disagree.
chatter_rendering='
import json, sys


def chatter(body, issue, when=""):
    """The rendering the answer at <body> carries, or None after saying why it has none."""
    which = "for issue %s%s" % (issue, " " + when if when else "")
    try:
        with open(body) as f:
            got = json.load(f)
    except ValueError:
        with open(body) as f:
            print("chatter_json %s returned something that is not JSON; it starts: %r"
                  % (which, f.read()[:200]))
        return None
    if not isinstance(got, dict) or "chatter" not in got:
        print("chatter_json %s returned %s; want an object with a \"chatter\" key"
              % (which, json.dumps(got, sort_keys=True)[:300]))
        return None
    # The rendering as the renderer’s own text or as its lines, since one line per thing said
    # or done is what the renderer promises and a list of them says the same thing.
    text = got["chatter"]
    if isinstance(text, list):
        text = "\n".join(str(line) for line in text)
    if not isinstance(text, str):
        print("chatter_json %s returned chatter=%s; want the rendered log as text or as its "
              "lines" % (which, json.dumps(text, sort_keys=True)[:300]))
        return None
    return text.strip("\n")


def want(path):
    """render-leaf-log.sh’s own rendering of a fixture, stripped the way an answer is."""
    with open(path) as f:
        return f.read().strip("\n")
'

# want_rendering <fixture> <want> <what> — render <fixture> with render-leaf-log.sh itself and
# leave its answer on <want>, or file the refusal as this case's problem. Every Chatter case
# compares against the renderer's own answer rather than a second spelling of its rules — a
# case that spelled them again would pass a pane that rendered the log its own way — so all
# five of those renderings go through here, and <what> names which fixture went unrendered.
want_rendering() {  # want_rendering <fixture> <want> <what>
  "$HERE/../render-leaf-log.sh" < "$1" > "$2" 2>/dev/null ||
    problems+=("render-leaf-log.sh could not render $3, which this case compares against")
}

# chatter_answer <repo> <issue> <tag> — ask <repo>'s chatter_json about <issue> once and leave
# the answer it wrote on `$answer`, or leave `$answer` empty after filing why the case has none
# to compare: the module never loaded, a fixture this case needs was already a problem, or the
# call raised and wrote nothing. Every Chatter case that asks once shares this half; what
# differs between them is only what they compare the answer to. The one that asks twice over a
# run that moves between the two calls spells its own, since what it pins is what happens in
# between.
chatter_answer() {  # chatter_answer <repo> <issue> <tag>
  local repo="$1" issue="$2" tag="$3" err="$work/$3.err"
  answer=""
  if [[ -n "$module_problem" ]]; then
    problems+=("$module_problem")
    return
  fi
  [[ "${#problems[@]}" -eq 0 ]] || return
  call_endpoint "$repo" chatter_json "$err" "{\"issue\": [\"$issue\"]}" "$work/$tag-$issue.json"
  if [[ ! -f "$work/$tag-$issue.json" ]]; then
    problems+=("calling $module.chatter_json wrote nothing: $(tail -n 1 "$err")")
    return
  fi
  answer="$work/$tag-$issue.json"
}

# The ledger and spec every Tests case fabricates before an endpoint will answer about its
# run: the `.tdd/issue-<n>.md` run_for_issue looks for, and the `.tdd/issue-<n>-spec.md` whose
# `Test command:` line tests_json reads. Those two facts are the whole of what any case here
# reads out of either file — the title, the step and the spec's prose are flavour — so the
# pair is written in one place, and a case names only what it varies: which run, which issue,
# and the test command when it is not `make test`.
fabricate_plan() {  # fabricate_plan <run> <n> <title> <step> [<test-command>]
  cat > "$1/.tdd/issue-$2.md" <<EOF
# Plan for #$2 — $3

- [ ] $4
EOF
  cat > "$1/.tdd/issue-$2-spec.md" <<EOF
## What to build

${4^}.

Test command: ${5:-make test}
EOF
}

# The `test-run` marks the two mark-reading cases below fabricate, written the way
# timed-test-run.sh appends them (timed-test-run.sh:45): a step-start mark first, so a log
# line that is no test run is there to be left out, then three test runs disagreeing on both
# axes the pane reports — a whole-suite run that passed, a named-suite run that failed, and a
# named-suite run that passed. One case counts those marks and the other reads the fields off
# them, so the log they share is written here once.
fabricate_marks() {  # fabricate_marks <run> <n> <step> <failed-suite> <passed-suite>
  local now; now="$(date +%s)"
  cat > "$1/.tdd/events.jsonl" <<EOF
{"ts": $((now - 300)), "issue": "$2", "actor": "conductor", "phase": "", "step": "$3", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((now - 240)), "issue": "$2", "actor": "", "phase": "", "step": "$3", "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": "fast", "suites": "", "seconds": "3", "status": "0"}
{"ts": $((now - 180)), "issue": "$2", "actor": "", "phase": "", "step": "$3", "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": "affected", "suites": "$4", "seconds": "9", "status": "1"}
{"ts": $((now - 120)), "issue": "$2", "actor": "", "phase": "", "step": "$3", "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": "target", "suites": "$5", "seconds": "8", "status": "0"}
EOF
}

# --- no argument: the page at / on the default port, and exit 0 on SIGINT ---
name="dashboard.sh with no argument serves the page at / on port 8765 and exits 0 when sent SIGINT"
problems=()
served="$(repo served)"
log="$work/served.log"

problem="$(port_problem "$PORT")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch "$DASH" "$served" "$log"
  dash_pid=$!

  url="http://127.0.0.1:$PORT/"
  page="$(serve_until_up "$url")"
  problem="$(answer_problem "$url" "$log" "$page")"

  if [[ -n "$problem" ]]; then
    problems+=("$problem")
  else
    ctype="$(http_ctype "$page")"
    body="$(http_body "$page")"
    [[ "$ctype" == text/html* ]] || problems+=("GET / is Content-Type '$ctype', want text/html")
    # The one HTML page, asked of it as the two things any HTML document has and a JSON
    # body or an error page does not. Not the page's contents: what it holds is the later
    # steps' business, and this step only pins that / is where it is served from.
    for want in "<html" "</html>"; do
      [[ "$body" == *"$want"* ]] ||
        problems+=("the body of GET / has no '$want'; it starts: $(printf '%q' "${body:0:200}")")
    done
  fi

  # The other half of the criterion: SIGINT, and an exit status of 0 — a server killed by
  # the signal it is meant to shut down on comes back 130, and that is a distinct failure
  # from never having served the page.
  stop "$dash_pid" && int_code=0 || int_code=$?
  [[ "$int_code" -eq 0 ]] || problems+=("exited $int_code after SIGINT, want 0")
fi

report "$name"

# --- make test runs this suite ---
# The roster is read off `make -n test` from the repository root, the way suite-lanes.test.sh
# reads it: make prints the recipe with its `$(TESTS)` glob expanded and runs nothing, so what
# it lists is exactly what `make test` would run — and a Makefile whose glob stopped reaching
# this directory, or that filtered this suite out, fails here rather than silently dropping it.
name="make test runs this suite"
problems=()
root="$(cd "$HERE/../../../.." && pwd)"
roster="$(make --no-print-directory -n -C "$root" test 2>&1)"
if ! grep -q 'skills/tdd/scripts/tests/dashboard\.test\.sh' <<< "$roster"; then
  problems+=("make -n test in $root does not name skills/tdd/scripts/tests/dashboard.test.sh, so make test never runs this suite")
fi

report "$name"

# --- an argument: that port, no interface but loopback, and every pane endpoint of one life ---
# One running server, three questions (#330: the suite's second and last server start). The
# page has to answer on the port the argument named (not the default); the same port has to
# refuse a connection made to this machine's other address; and the same process has to go on
# answering each of the three pane endpoints with the JSON document that pane reads, so a
# server that answered its first request and then stopped serving, or that could only be asked
# one question per life, fails here. Two servers could not answer the loopback question together
# — a second one on the same port would fail to bind — so it is one launch. What each payload
# holds is asked of runs_json, metrics_json and events_json directly below; the one payload
# fact only a live server has is that /api/runs's `elapsed_seconds` is counted, so the Runs
# answer is also compared with `status.sh --json` here, that field as numbers seconds apart.
name="dashboard.sh with a port argument serves the page on that port, binds 127.0.0.1 only, and answers every pane endpoint with JSON"
problems=()
arg_repo="$(repo argport)"
arg_log="$work/argport.log"
arg_run="$(fabricate_run "$arg_repo" 51 tdd/51-lamps-hum)"
cat > "$arg_run/.tdd/issue-51.md" <<'EOF'
# Plan for #51 — lamps hum

- [x] a lamp exists
- [ ] a lamp hums
EOF
arg_now="$(date +%s)"
cat > "$arg_run/.tdd/events.jsonl" <<EOF
{"ts": $((arg_now - 120)), "issue": "51", "actor": "conductor", "phase": "", "step": "a lamp hums", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((arg_now - 110)), "issue": "51", "actor": "developer", "phase": "red", "step": "a lamp hums", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((arg_now - 60)), "issue": "51", "actor": "developer", "phase": "red", "step": "a lamp hums", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "0.25", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500"}
EOF
arg_port="$(free_port)"

problem="$(port_problem "$arg_port")"
if [[ -z "$problem" && "$arg_port" == "$PORT" ]]; then
  problem="the kernel handed out $arg_port, which is the default port: a server ignoring its argument would look right, so this case cannot run on it"
fi
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch "$DASH" "$arg_repo" "$arg_log" "$arg_port"
  arg_pid=$!

  # The URL is the port the argument named, so anything wrong with the fetch of it is the
  # first half of the criterion failing: the server did not bind the port it was given.
  # Nothing here reads the body — that the page is served at / is the case above.
  arg_url="http://127.0.0.1:$arg_port/"
  arg_page="$(serve_until_up "$arg_url")"
  problem="$(answer_problem "$arg_url" "$arg_log" "$arg_page")"
  [[ -z "$problem" ]] || problems+=("$problem")

  # The other interface. Fails closed when this machine has no non-loopback address: a case
  # that quietly skipped the half it exists to ask would report a pass for a server bound to
  # 0.0.0.0.
  elsewhere="$(other_addr)"
  if [[ -z "$elsewhere" ]]; then
    problems+=("this machine has no non-loopback IPv4 address, so 'binds 127.0.0.1 only' could not be asked of it")
  elif reachable "$elsewhere" "$arg_port"; then
    problems+=("the server answered on $elsewhere:$arg_port as well, so it is bound to every interface; want 127.0.0.1 only")
  fi

  # status.sh's own answer, asked from the same repository and with the same environment the
  # launch gave the server, so any difference is the endpoint's.
  (cd "$arg_repo" && PYTHONPATH= PYTHONNOUSERSITE=1 "$STATUS" --json) \
    > "$work/argport-status.json" 2>/dev/null
  for path in /api/runs /api/metrics "/api/events?issue=51"; do
    url="http://127.0.0.1:$arg_port$path"
    answer="$(serve_until_up "$url")"
    problem="$(answer_problem "$url" "$arg_log" "$answer")"
    if [[ -n "$problem" ]]; then
      problems+=("$problem")
      continue
    fi
    http_body "$answer" > "$work/argport.json"
    add_problems < <(python3 -c '
import json, sys

path, body, status_path = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(body) as f:
        got = json.load(f)
except ValueError:
    with open(body) as f:
        print("GET %s is not JSON; it starts: %r" % (path, f.read()[:200]))
    sys.exit()
want = {"/api/runs": ("runs", list), "/api/metrics": ("issues", dict),
        "/api/events?issue=51": ("events", list)}[path]
key, kind = want
if not isinstance(got, dict) or not isinstance(got.get(key), kind):
    print("GET %s returned %s; want an object with a %r %s"
          % (path, json.dumps(got, sort_keys=True)[:300], key, kind.__name__))
    sys.exit()
if not got[key]:
    print("GET %s returned an empty %r for a repository with run #51 in it" % (path, key))
    sys.exit()
if path != "/api/runs":
    sys.exit()

# `elapsed_seconds` is `now` minus the leaf launch, measured once when the endpoint answers
# and again when status.sh ran above, so it is compared as numbers seconds apart rather than
# dropped: dropping it would let an endpoint that never reports elapsed time pass.
with open(status_path) as f:
    status = json.load(f)


def without_elapsed(doc):
    out = json.loads(json.dumps(doc))
    for run in out.get("runs", []) if isinstance(out.get("runs"), list) else []:
        if isinstance(run, dict):
            run.pop("elapsed_seconds", None)
    return out


if without_elapsed(got) != without_elapsed(status):
    print("GET /api/runs returned %s" % json.dumps(without_elapsed(got), sort_keys=True))
    print("status.sh --json returns %s" % json.dumps(without_elapsed(status), sort_keys=True))
    sys.exit()
for i, (g, w) in enumerate(zip(got["runs"], status["runs"])):
    if "elapsed_seconds" not in g:
        print("run %d has no elapsed_seconds from GET /api/runs; status.sh --json "
              "reports %s" % (i, w.get("elapsed_seconds")))
    elif abs(int(g["elapsed_seconds"]) - int(w["elapsed_seconds"])) > 10:
        print("run %d elapsed_seconds is %s from GET /api/runs and %s from status.sh --json, "
              "more than the 10 s the two calls can be apart"
              % (i, g["elapsed_seconds"], w["elapsed_seconds"]))
' "$path" "$work/argport.json" "$work/argport-status.json")
  done

  stop "$arg_pid" || :
fi

report "$name"

# --- the two server starts, together: every lifecycle fact asked of a live process ---
# Right after the second of them on purpose (#330): the payloads and the page moved to a
# function or a file, so what only a process can answer — the default port, a port argument,
# loopback only, exit 0 on SIGINT, one process answering more than one request — has to be
# answered by the two starts above and nothing else. Read off what they left behind: the
# port each start's python3 was handed, on the shim's $starts log; the answers each fetched
# and the status the first exited with; and the problems the second collected, still in
# `problems` here, for the one fact — refused on another interface — that leaves no answer.
# A fact neither start answered fails here by name, even when both cases above passed.
name="the two dashboard.sh servers together answer on 8765 with no argument, on a port argument instead, on loopback only, exit 0 on SIGINT, and one of them answers more than once"
arg_problems=("${problems[@]}")
problems=()
start_ports="$(awk '{ print $3 }' "$starts")"
starts_on() { grep -cx -- "$1" <<< "$start_ports" || :; }

if [[ "$(starts_on "$PORT")" -ne 1 ]]; then
  problems+=("$(starts_on "$PORT") server starts were handed port $PORT, want 1 — the start with no argument; ports handed: $(tr '\n' ' ' <<< "$start_ports")")
elif [[ "$(http_status "${page:-}")" != 200 ]]; then
  problems+=("the start with no argument never answered 200 at http://127.0.0.1:$PORT/, so port $PORT as the default was not asked of a live server")
fi
if [[ "${int_code:-unset}" != 0 ]]; then
  problems+=("the start with no argument exited ${int_code:-unset} after SIGINT, want 0")
fi

if [[ -z "${arg_port:-}" || "$arg_port" == "$PORT" ]]; then
  problems+=("the start with an argument was handed '${arg_port:-}', want a port other than $PORT")
elif [[ "$(starts_on "$arg_port")" -ne 1 ]]; then
  problems+=("$(starts_on "$arg_port") server starts were handed port $arg_port, want 1 — the start with an argument; ports handed: $(tr '\n' ' ' <<< "$start_ports")")
elif [[ "$(http_status "${arg_page:-}")" != 200 ]]; then
  problems+=("the start with an argument never answered 200 at http://127.0.0.1:$arg_port/, so the port argument was not asked of a live server")
elif [[ "$(http_status "${answer:-}")" != 200 ]]; then
  problems+=("the start with an argument answered its page but not a later request, so no one process was seen answering more than once")
fi

if [[ -z "${elsewhere:-}" ]]; then
  problems+=("no non-loopback address was probed against the start with an argument, so 'loopback only' was not asked of a live server")
else
  for line in "${arg_problems[@]}"; do
    [[ "$line" == *"answered on $elsewhere:"* ]] && problems+=("loopback only did not hold: $line")
  done
fi

report "$name"

# --- the server's python is a module beside dashboard.sh, and importing it binds nothing ---
# The endpoints are pure functions of the filesystem and of status.sh/metrics.sh, so a case
# should be able to ask one a question without starting a server (#330). That needs the python
# to be a file on disk dashboard.sh execs, not a heredoc on its stdin, and the file to bind its
# port only when run as the program, never when imported. The module is the one found at the
# top of the suite. It is imported with the argv dashboard.sh hands
# when started with no port argument, so the port it would bind is the default: the port asked about
# afterwards is the one an unguarded bootstrap would have taken. That question is asked inside
# the importing process, while the module is still loaded — after it exits, whatever it bound
# is released and the answer would say nothing. An alarm that raises bounds the whole of it,
# because an import that falls into serve_forever never returns on its own; the process says
# `checked` last, so one that died on the way is a failure and not a silent pass.
name="importing the dashboard's python module and calling its endpoint functions never binds port 8765"
problems=()
imported="$(repo imported)"

problem="$(port_problem "$PORT")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  if [[ -n "$module_problem" ]]; then
    problems+=("$module_problem")
  elif [[ ! -f "$scripts/$module.py" ]]; then
    problems+=("dashboard.sh execs $module.py, but there is no such file beside it")
  else
    checked=""
    while IFS= read -r line; do
      if [[ "$line" == checked ]]; then
        checked=1
      elif [[ -n "$line" ]]; then
        problems+=("$line")
      fi
    done < <(cd "$imported" && PYTHONPATH= PYTHONNOUSERSITE=1 python3 -c '
import importlib, signal, socket, sys

scripts, module, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
def timed_out(signum, frame):
    raise TimeoutError("still running after 10 s")
signal.signal(signal.SIGALRM, timed_out)
signal.alarm(10)
sys.path.insert(0, scripts)
sys.argv = [scripts + "/" + module + ".py", scripts + "/dashboard.html", str(port),
            scripts + "/status.sh", scripts + "/metrics.sh"]
try:
    mod = importlib.import_module(module)
    for fn, query in (("runs_json", {}), ("metrics_json", {}), ("events_json", {"issue": [""]})):
        if not callable(getattr(mod, fn, None)):
            print("%s.py has no function %s" % (module, fn))
            continue
        getattr(mod, fn)(query)
except BaseException as e:
    print("importing %s.py and calling its endpoints raised %s: %s" % (module, type(e).__name__, e))
s = socket.socket(); s.settimeout(1.0)
if s.connect_ex(("127.0.0.1", port)) == 0:
    print("port %d answers after importing %s.py and calling its endpoints; want it still free" % (port, module))
print("checked")
' "$scripts" "$module" "$PORT")
    [[ -n "$checked" ]] ||
      problems+=("the process importing $module.py died before it could ask whether port $PORT is free")
  fi
fi

report "$name"

# --- the Runs endpoint's payload, asked of runs_json directly: status.sh --json, byte for byte ---
# The Runs pane is a reader of `status.sh --json`, so the criterion is an equality, asked of the
# function that answers the endpoint rather than of a server answering it (#330): the module is
# imported the way the case above imports it, runs_json is called in the fixture repository, and what it returns is
# compared with what `status.sh --json` prints there, byte for byte. No dashboard.sh is started
# and no socket is opened, so nothing here waits on a server coming up.
#
# Byte-identical is only a fair ask of a fixture with no clock in its answer, so the run here has
# a ledger and no event log: status.sh then reports its issue, title, branch and step and no
# `elapsed_seconds`, which would otherwise count the gap between the two calls.
name="runs_json, called directly, returns status.sh --json byte for byte"
problems=()
direct_repo="$(repo runsdirect)"
direct_run="$(fabricate_run "$direct_repo" 22 tdd/22-lamps-glow)"
cat > "$direct_run/.tdd/issue-22.md" <<'EOF'
# Plan for #22 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$direct_repo" runs_json "$work/runs-direct.err" '{}' "$work/runs-direct.json"
  (cd "$direct_repo" && PYTHONPATH= PYTHONNOUSERSITE=1 "$STATUS" --json) \
    > "$work/runs-direct-status.json" 2>/dev/null
  if [[ ! -f "$work/runs-direct.json" ]]; then
    problems+=("calling $module.runs_json wrote nothing: $(tail -n 1 "$work/runs-direct.err")")
  elif ! cmp -s "$work/runs-direct.json" "$work/runs-direct-status.json"; then
    problems+=("runs_json returned $(printf '%q' "$(cat "$work/runs-direct.json")")")
    problems+=("status.sh --json prints $(printf '%q' "$(cat "$work/runs-direct-status.json")")")
  elif [[ ! -s "$work/runs-direct-status.json" ]]; then
    problems+=("status.sh --json printed nothing for the fixture, so the equality says nothing")
  fi
fi

report "$name"

# --- the Metrics endpoint's payload, asked of metrics_json directly: live and committed ---
# The Metrics pane's two equalities — live for a running run, the committed report for a
# finished one (SKILL.md:858) — asked of the function that answers the endpoint rather than of a server answering it (#330): a running run's report is
# what metrics.sh prints for it, recomputed, and a finished run's is its committed
# `.tdd/issue-<n>-metrics.md` verbatim. Both runs carry a committed report that metrics.sh
# would never print, so a function that read the file for both fails on the running run and
# one that recomputed both fails on the finished one. The module is imported the way the
# runs_json case above imports it, in the fixture repository, and no dashboard.sh is started.
name="metrics_json, called directly, recomputes a running run and returns the committed report for a finished one"
problems=()
mdirect_repo="$(repo metricsdirect)"

mdirect_live="$(fabricate_run "$mdirect_repo" 31 tdd/31-lamps-glow)"
cat > "$mdirect_live/.tdd/issue-31.md" <<'EOF'
# Plan for #31 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
mdirect_now="$(date +%s)"
cat > "$mdirect_live/.tdd/events.jsonl" <<EOF
{"ts": $((mdirect_now - 120)), "issue": "31", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((mdirect_now - 110)), "issue": "31", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((mdirect_now - 60)), "issue": "31", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "0.25", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500", "num_turns": "7", "duration_api_ms": "12000"}
EOF
cat > "$mdirect_live/.tdd/issue-31-metrics.md" <<'EOF'
# a stale committed report for #31 that metrics.sh would never print
EOF

mdirect_done="$(fabricate_run "$mdirect_repo" 32 tdd/32-lamps-dim)"
cat > "$mdirect_done/.tdd/issue-32.md" <<'EOF'
# Plan for #32 — lamps dim

- [x] a lamp exists
- [x] a lamp dims
EOF
cat > "$mdirect_done/.tdd/events.jsonl" <<EOF
{"ts": $((mdirect_now - 9000)), "issue": "32", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((mdirect_now - 8900)), "issue": "32", "actor": "developer", "phase": "green", "step": "a lamp dims", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green"}
{"ts": $((mdirect_now - 8800)), "issue": "32", "actor": "verifier", "phase": "green", "step": "a lamp dims", "event": "verdict", "attempt": "1", "skill_commit": "abc", "verdict": "PASS"}
{"ts": $((mdirect_now - 8700)), "issue": "32", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-done", "attempt": "", "skill_commit": "abc"}
{"ts": $((mdirect_now - 8600)), "issue": "32", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://example.invalid/pr/2"}
EOF
cat > "$mdirect_done/.tdd/issue-32-metrics.md" <<'EOF'
# What solving #32 cost — the committed report, verbatim

| phase | attempts |
|---|---|
| green | 1 |
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$mdirect_repo" metrics_json "$work/metrics-direct.err" '{}' "$work/metrics-direct.json"
  # metrics.sh's own answer for the running run, asked from that run's worktree the way the
  # conductor asks it, so a difference is the function's and not the fixture's.
  (cd "$mdirect_live" && PYTHONPATH= PYTHONNOUSERSITE=1 "$METRICS" 31) \
    > "$work/metrics-direct-live.md" 2>/dev/null
  if [[ ! -f "$work/metrics-direct.json" ]]; then
    problems+=("calling $module.metrics_json wrote nothing: $(tail -n 1 "$work/metrics-direct.err")")
  else
    add_problems < <(python3 -c "$metrics_issues"'
live_path, committed_path = sys.argv[3], sys.argv[4]
with open(live_path) as f:
    live = f.read()
with open(committed_path) as f:
    committed = f.read()
if not live:
    print("metrics.sh 31 printed nothing for the running run, so the equality says nothing")
if issues["31"] != live:
    print("issue 31 is running, so its report has to be recomputed from the event log: "
          "metrics_json returned %r, and metrics.sh 31 prints %r"
          % (issues["31"][:300], live[:300]))
if issues["32"] != committed:
    print("issue 32 ended with a done mark, so its report has to be the committed "
          ".tdd/issue-32-metrics.md: metrics_json returned %r, and the committed file holds "
          "%r" % (issues["32"][:300], committed[:300]))
' "$work/metrics-direct.json" 31,32 "$work/metrics-direct-live.md" \
      "$mdirect_done/.tdd/issue-32-metrics.md")
  fi
fi

report "$name"

# --- the Metrics endpoint's payload for a BAILED run: the committed report, verbatim ---
# A run can end two ways, and the pane's reading has to be the same for both: `done` and
# `bail` are the pair that ends a log (status.sh:76), and the Bailing procedure commits
# `.tdd/issue-<n>-metrics.md` before the push exactly as draft-PR time does (SKILL.md:858).
# So a run whose log ends in a `bail` mark is quoted, not recomputed — asked of metrics_json
# directly (#330), with no dashboard.sh started. The committed report here is a sentence
# metrics.sh would never print, so a function that recomputed a bailed run fails the equality
# rather than passing on a coincidence.
name="metrics_json, called directly, returns the committed report for a run that ended in a bail mark"
problems=()
mbail_repo="$(repo metricsbail)"

mbail_run="$(fabricate_run "$mbail_repo" 33 tdd/33-lamps-flicker)"
cat > "$mbail_run/.tdd/issue-33.md" <<'EOF'
# Plan for #33 — lamps flicker

- [x] a lamp exists
- [ ] a lamp flickers
EOF
mbail_now="$(date +%s)"
cat > "$mbail_run/.tdd/events.jsonl" <<EOF
{"ts": $((mbail_now - 9000)), "issue": "33", "actor": "conductor", "phase": "", "step": "a lamp flickers", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((mbail_now - 8900)), "issue": "33", "actor": "developer", "phase": "red", "step": "a lamp flickers", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((mbail_now - 8800)), "issue": "33", "actor": "conductor", "phase": "red", "step": "a lamp flickers", "event": "bail", "attempt": "1", "skill_commit": "abc", "reason": "killed-stuck"}
EOF
cat > "$mbail_run/.tdd/issue-33-metrics.md" <<'EOF'
# What solving #33 cost — the committed report of a bailed run, verbatim

| phase | attempts |
|---|---|
| red | 1 |
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$mbail_repo" metrics_json "$work/metrics-bail.err" '{}' "$work/metrics-bail.json"
  if [[ ! -f "$work/metrics-bail.json" ]]; then
    problems+=("calling $module.metrics_json wrote nothing: $(tail -n 1 "$work/metrics-bail.err")")
  else
    add_problems < <(python3 -c "$metrics_issues"'
with open(sys.argv[3]) as f:
    committed = f.read()
if issues["33"] != committed:
    print("issue 33 ended with a bail mark, so its report has to be the committed "
          ".tdd/issue-33-metrics.md verbatim: metrics_json returned %r, and the committed "
          "file holds %r" % (issues["33"][:300], committed[:300]))
' "$work/metrics-bail.json" 33 "$mbail_run/.tdd/issue-33-metrics.md")
  fi
fi

report "$name"

# --- the Metrics endpoint's payload for an ended run whose committed report is MISSING ---
# Both endings commit `.tdd/issue-<n>-metrics.md` before the run stops, but a bail that never
# reached that step of the Bailing procedure leaves a run whose log says ended and whose report
# is not there. `run_ended` is still true, so the pane quotes a file that does not exist — and
# quoting nothing reads on the page as "this run had nothing to report" rather than "the report
# is missing". So the reading for that run is a marker: never the empty string, and naming the
# file that is not there, which is the whole of what tells it apart from a real empty report.
# Asked of metrics_json directly (#330), with no dashboard.sh started; the run carries no
# committed report at all, so a function that returned the file's contents has nothing to
# return and only a marker can pass.
name="metrics_json, called directly, reports a marker for an ended run whose committed metrics file is missing"
problems=()
mgone_repo="$(repo metricsgone)"

mgone_run="$(fabricate_run "$mgone_repo" 34 tdd/34-lamps-gutter)"
cat > "$mgone_run/.tdd/issue-34.md" <<'EOF'
# Plan for #34 — lamps gutter

- [x] a lamp exists
- [ ] a lamp gutters
EOF
mgone_now="$(date +%s)"
cat > "$mgone_run/.tdd/events.jsonl" <<EOF
{"ts": $((mgone_now - 9000)), "issue": "34", "actor": "conductor", "phase": "", "step": "a lamp gutters", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((mgone_now - 8900)), "issue": "34", "actor": "developer", "phase": "red", "step": "a lamp gutters", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((mgone_now - 8800)), "issue": "34", "actor": "conductor", "phase": "red", "step": "a lamp gutters", "event": "bail", "attempt": "1", "skill_commit": "abc", "reason": "killed-stuck"}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
elif [[ -e "$mgone_run/.tdd/issue-34-metrics.md" ]]; then
  problems+=("the fixture run has a committed .tdd/issue-34-metrics.md, so the case says nothing")
else
  call_endpoint "$mgone_repo" metrics_json "$work/metrics-gone.err" '{}' "$work/metrics-gone.json"
  if [[ ! -f "$work/metrics-gone.json" ]]; then
    problems+=("calling $module.metrics_json wrote nothing: $(tail -n 1 "$work/metrics-gone.err")")
  else
    add_problems < <(python3 -c "$metrics_issues"'
report = issues["34"]
if not report.strip():
    print("issue 34 ended with a bail mark and has no committed "
          ".tdd/issue-34-metrics.md, so its report has to be a marker a viewer can tell "
          "apart from a real empty report: metrics_json returned %r" % report)
elif "issue-34-metrics.md" not in report:
    print("issue 34 has no committed .tdd/issue-34-metrics.md, so its report has to name "
          "the file that is missing: metrics_json returned %r" % report[:300])
' "$work/metrics-gone.json" 34)
  fi
fi

report "$name"

# --- run_ended for a STOPPED run: not ended, so the Metrics pane keeps recomputing it ---
# A stop mark (#388) is not the third ending beside `done` and `bail`: a stopped run is
# resumed, commits no report, and is still spending, so the pair that splits recomputed from
# quoted stays the pair it was (#390). Asked of run_ended directly, with no dashboard.sh
# started, over a log that carries a stop mark and neither of the two that end a run.
name="run_ended, called directly, answers false for a run whose log carries a stop mark and no done or bail"
problems=()
rstop_repo="$(repo runendedstop)"

rstop_run="$(fabricate_run "$rstop_repo" 35 tdd/35-lamps-glow)"
rstop_now="$(date +%s)"
cat > "$rstop_run/.tdd/events.jsonl" <<EOF
{"ts": $((rstop_now - 9000)), "issue": "35", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((rstop_now - 8900)), "issue": "35", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((rstop_now - 8800)), "issue": "35", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "stop", "attempt": "", "skill_commit": "abc", "mode": "at-leaf", "at": "planned"}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  add_problems < <(cd "$rstop_repo" && PYTHONPATH= PYTHONNOUSERSITE=1 python3 -c '
import importlib, sys

scripts, module, port, run = sys.argv[1:5]
sys.path.insert(0, scripts)
sys.argv = [scripts + "/" + module + ".py", scripts + "/dashboard.html", port,
            scripts + "/status.sh", scripts + "/metrics.sh"]
answer = importlib.import_module(module).run_ended(run)
if answer is not False:
    print("issue 35 logged a stop mark and no done or bail, so it has not ended and its "
          "report must be recomputed: run_ended returned %r, want False" % (answer,))
' "$scripts" "$module" "$PORT" "$rstop_run" 2>&1)
fi

report "$name"

# --- the Metrics endpoint keys a run by its own directory, and runs metrics.sh once for it ---
# Ledgers are committed, so a run worktree carries a copy of every earlier issue's plan: the
# run under `.tdd/wt/7/` here holds issue-3.md and issue-5.md beside its own issue-7.md. The
# rule the criterion names is the directory, not the glob — `.tdd/wt/<n>/` is issue `<n>`, and
# its ledger is `.tdd/issue-<n>.md` — so the payload has exactly one entry, keyed 7, and
# metrics.sh is run exactly once, for 7, in that directory.
#
# The call count IS the behaviour here, so it is pinned with an in-process spy rather than a
# PATH shim counting processes: `capture` is the one wrapper every shell-out in the module goes
# through, and the case replaces it with a same-named function that records the metrics.sh
# calls and answers them with a stub. Everything else — the `git worktree list` that finds the
# runs — still goes to the real one, so what is faked is only the script whose calls are counted.
# The directory a call was made in is compared as a real path: the runs are found through git,
# which resolves `/var` to `/private/var` on a Mac, and the same directory spelled two ways
# would otherwise fail a correct implementation.
name="metrics_json keys one entry per run directory by its own issue number and runs metrics.sh once for a live run"
problems=()
mown_repo="$(repo metricsown)"
mown_run="$(fabricate_run "$mown_repo" 7 tdd/7-lamps-glow)"
cat > "$mown_run/.tdd/issue-7.md" <<'EOF'
# Plan for #7 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
# The earlier runs' committed plans, which differ from each other in nothing the rule reads:
# the criterion is that a ledger which is not this directory's own is passed over, whatever it
# says, so what each of them says is the same sentence.
for mown_other in 3 5; do
  cat > "$mown_run/.tdd/issue-$mown_other.md" <<EOF
# Plan for #$mown_other — an earlier run's committed plan

- [x] a lamp is wired
EOF
done
mown_now="$(date +%s)"
cat > "$mown_run/.tdd/events.jsonl" <<EOF
{"ts": $((mown_now - 120)), "issue": "7", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((mown_now - 110)), "issue": "7", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  add_problems < <(cd "$mown_repo" && PYTHONPATH= PYTHONNOUSERSITE=1 python3 -c '
import importlib, json, os, sys

scripts, module, port, run = sys.argv[1:5]
run = os.path.realpath(run)
sys.path.insert(0, scripts)
sys.argv = [scripts + "/" + module + ".py", scripts + "/dashboard.html", port,
            scripts + "/status.sh", scripts + "/metrics.sh"]
mod = importlib.import_module(module)

metrics_calls = []
real_capture = mod.capture

def spy(argv, cwd=None):
    if list(argv)[:1] == [mod.metrics_sh]:
        metrics_calls.append([list(argv), os.path.realpath(cwd) if cwd else cwd])
        return b"a stub report\n"
    return real_capture(argv, cwd=cwd)

mod.capture = spy
got = json.loads(mod.metrics_json({}))
issues = got.get("issues", {}) if isinstance(got, dict) else {}
if sorted(issues) != ["7"]:
    print("metrics_json reports issues %s; want 7 alone, the issue the run directory "
          ".tdd/wt/7 is for: issue-3.md and issue-5.md there are earlier runs committed "
          "plans" % json.dumps(sorted(issues)))
if metrics_calls != [[[mod.metrics_sh, "7"], run]]:
    print("metrics_json ran metrics.sh as %s; want exactly one run of it, for issue 7 in %s"
          % (json.dumps([[a[1:], c] for a, c in metrics_calls]), run))
' "$scripts" "$module" "$PORT" "$mown_run")
fi

report "$name"

# --- the Events endpoint's payload, asked of events_json directly: the selected run, or nothing ---
# The Events pane's contract — the selected run's log, newest last — asked of the function that
# answers the endpoint rather than of a server answering it (#330): events_json is handed the query string
# the endpoint parses, `?issue=41` read as {"issue": ["41"]}, and returns a contiguous suffix of
# that run's `.tdd/events.jsonl` ending at its newest line. A second run's log is there and must
# not be answered with. And an issue no run holds a ledger for — 99 here — is the empty list,
# not another run's log and not an error. The module is imported the way the runs_json case
# above imports it, in the fixture repository, and no dashboard.sh is started.
name="events_json, called directly, returns the selected run's events newest last, and none for an issue no run holds"
problems=()
edirect_repo="$(repo eventsdirect)"

edirect_sel="$(fabricate_run "$edirect_repo" 51 tdd/51-lamps-flicker)"
cat > "$edirect_sel/.tdd/issue-51.md" <<'EOF'
# Plan for #51 — lamps flicker

- [x] a lamp exists
- [ ] a lamp flickers
EOF
edirect_now="$(date +%s)"
: > "$edirect_sel/.tdd/events.jsonl"
for i in $(seq 1 30); do
  printf '{"ts": %s, "issue": "51", "actor": "developer", "phase": "red", "step": "a lamp flickers", "event": "launch", "attempt": "%s", "skill_commit": "abc", "name": "develop-red", "seq": %s}\n' \
    "$((edirect_now - 3000 + i * 10))" "$i" "$i" >> "$edirect_sel/.tdd/events.jsonl"
done

edirect_other="$(fabricate_run "$edirect_repo" 52 tdd/52-lamps-dim)"
cat > "$edirect_other/.tdd/issue-52.md" <<'EOF'
# Plan for #52 — lamps dim

- [ ] a lamp dims
EOF
cat > "$edirect_other/.tdd/events.jsonl" <<EOF
{"ts": $((edirect_now - 200)), "issue": "52", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((edirect_now - 100)), "issue": "52", "actor": "developer", "phase": "green", "step": "a lamp dims", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green", "seq": 2}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$edirect_repo" events_json "$work/events-direct.err" \
    '{"issue": ["51"]}' "$work/events-direct-51.json" \
    '{"issue": ["99"]}' "$work/events-direct-99.json"
  if [[ ! -f "$work/events-direct-51.json" || ! -f "$work/events-direct-99.json" ]]; then
    problems+=("calling $module.events_json wrote nothing: $(tail -n 1 "$work/events-direct.err")")
  else
    add_problems < <(python3 -c "$events_answers"'
events, none = answers["51"], answers["99"]
if not events:
    print("events_json for issue 51 returned no events; the selected run’s log has %d" % len(want))
elif len(events) > len(want):
    print("events_json for issue 51 returned %d events; the selected run’s log has only %d"
          % (len(events), len(want)))
elif events != want[len(want) - len(events):]:
    print("events_json for issue 51 returned %s" % json.dumps(events, sort_keys=True)[:400])
    print("the last %d lines of the run’s log, newest last, are %s"
          % (len(events), json.dumps(want[len(want) - len(events):], sort_keys=True)[:400]))
if none != []:
    print("events_json for issue 99, which no run holds a ledger for, returned %s; want []"
          % json.dumps(none, sort_keys=True)[:400])
' "$work/events-direct-51.json" 51 "$work/events-direct-99.json" 99 \
      "$edirect_sel/.tdd/events.jsonl")
  fi
fi

report "$name"

# --- the Events endpoint answers by the run directory's own issue number ---
# The other half of the rule the Metrics case above pins, asked of the Events pane. Ledgers
# are committed, so the run under `.tdd/wt/7/` carries a copy of #3's plan; deciding which run
# an issue belongs to by who holds its ledger therefore answered `?issue=3` with run 7's log
# (#343). The directory is the rule — `.tdd/wt/<n>/` is issue `<n>` — so issue 3, which has no
# run directory of its own, is the empty list, and issue 7 is still its own run's events.
name="events_json answers by the run directory's own issue, so an issue present only as a committed ledger copy is the empty list"
problems=()
eown_repo="$(repo eventsown)"

eown_run="$(fabricate_run "$eown_repo" 7 tdd/7-lamps-glow)"
cat > "$eown_run/.tdd/issue-7.md" <<'EOF'
# Plan for #7 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
cat > "$eown_run/.tdd/issue-3.md" <<'EOF'
# Plan for #3 — an earlier run's committed plan

- [x] a lamp is wired
EOF
eown_now="$(date +%s)"
cat > "$eown_run/.tdd/events.jsonl" <<EOF
{"ts": $((eown_now - 120)), "issue": "7", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((eown_now - 110)), "issue": "7", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red", "seq": 2}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$eown_repo" events_json "$work/events-own.err" \
    '{"issue": ["3"]}' "$work/events-own-3.json" \
    '{"issue": ["7"]}' "$work/events-own-7.json"
  if [[ ! -f "$work/events-own-3.json" || ! -f "$work/events-own-7.json" ]]; then
    problems+=("calling $module.events_json wrote nothing: $(tail -n 1 "$work/events-own.err")")
  else
    add_problems < <(python3 -c "$events_answers"'
if answers["3"] != []:
    print("events_json for issue 3, which is only a committed ledger copy inside the run "
          "directory .tdd/wt/7, returned %s; want [], because there is no .tdd/wt/3"
          % json.dumps(answers["3"], sort_keys=True)[:400])
if answers["7"] != want:
    print("events_json for issue 7 returned %s; want its own run directory’s log, %s"
          % (json.dumps(answers["7"], sort_keys=True)[:400],
             json.dumps(want, sort_keys=True)[:400]))
' "$work/events-own-3.json" 3 "$work/events-own-7.json" 7 \
      "$eown_run/.tdd/events.jsonl")
  fi
fi

report "$name"

# --- the Tests endpoint's payload, asked of tests_json directly: the selected run's leaf test runs ---
# The Tests pane's contract — the test runs the LEAVES performed, read back out of their
# stream-json logs — asked of the function that answers the endpoint rather than of a server
# answering it, the way the events cases above ask theirs. tests_json is handed the parsed
# query string, `?issue=51` read as {"issue": ["51"]}, and returns one entry per Bash tool
# call in that run's leaf logs whose command is the run's own test command — the `Test
# command:` line of its `.tdd/issue-<n>-spec.md` — carrying that command, whether it passed
# (the tool result's exit status: `is_error` false is a pass, true a fail) and the tail of
# its output. A leaf's other Bash calls are no test run of the suite and are not listed, and
# a second run, whose leaf ran the same command, must not be answered with.
name="tests_json, called directly, lists the selected run's leaf test runs with command, pass/fail and output tail"
problems=()
tdirect_repo="$(repo testsdirect)"

tdirect_sel="$(fabricate_run "$tdirect_repo" 51 tdd/51-lamps-flicker)"
fabricate_plan "$tdirect_sel" 51 "lamps flicker" "a lamp flickers"
cat > "$tdirect_sel/.tdd/develop-red.out" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s1", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reading the suite before adding the case."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "git log --oneline -3", "description": "Recent commits"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_1", "type": "tool_result", "content": "abc1234 plan: a lamp flickers", "is_error": false}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_2", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_2", "type": "tool_result", "content": "FAIL - a lamp flickers\n----\n11 passed, 1 failed", "is_error": true}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_3", "name": "Bash", "input": {"command": "make test", "description": "Run the suite again"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_3", "type": "tool_result", "content": "----\n12 passed, 0 failed", "is_error": false}]}}
{"type": "result", "subtype": "success", "is_error": false, "result": "The case is added and fails as predicted."}
EOF

tdirect_other="$(fabricate_run "$tdirect_repo" 52 tdd/52-lamps-dim)"
fabricate_plan "$tdirect_other" 52 "lamps dim" "a lamp dims"
cat > "$tdirect_other/.tdd/develop-green.out" <<'EOF'
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_9", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_9", "type": "tool_result", "content": "----\n7 passed, 0 failed  (run 52)", "is_error": false}]}}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$tdirect_repo" tests_json "$work/tests-direct.err" \
    '{"issue": ["51"]}' "$work/tests-direct-51.json"
  if [[ ! -f "$work/tests-direct-51.json" ]]; then
    problems+=("calling $module.tests_json wrote nothing: $(tail -n 1 "$work/tests-direct.err")")
  else
    add_problems < <(python3 -c "$tests_runs"'
red_fail = "FAIL - a lamp flickers\n----\n11 passed, 1 failed"
red_pass = "----\n12 passed, 0 failed"
if len(runs) != 2:
    print("tests_json for issue 51 returned %d test runs, %s; want the two `make test` calls "
          "in its own leaf log — neither its `git log` call nor run 52\u2019s `make test`"
          % (len(runs), json.dumps(runs, sort_keys=True)[:400]))
    sys.exit()
for entry, passed, output in zip(runs, (False, True), (red_fail, red_pass)):
    if entry.get("command") != "make test":
        print("a test run came back with command %r; want the run’s own test command, "
              "`make test`" % entry.get("command"))
    if entry.get("passed") is not passed:
        print("the `make test` whose tool result is %r came back passed=%r; want %r, from that "
              "result’s exit status" % (output, entry.get("passed"), passed))
    tail = entry.get("tail")
    if not isinstance(tail, str) or not tail or not output.endswith(tail):
        print("the `make test` whose output is %r came back tail=%r; want a non-empty tail of "
              "that output" % (output, tail))
    elif output.splitlines()[-1] not in tail:
        print("the `make test` whose output is %r came back tail=%r; want it to carry that "
              "output’s last line, %r" % (output, tail, output.splitlines()[-1]))
' "$work/tests-direct-51.json" 51)
  fi
fi

report "$name"

# --- the Tests endpoint runs no suite: the test command is read, never executed ---
# The other half of the Tests pane's contract. What the pane lists is the runs the LEAVES
# performed, so the endpoint's own work is reading logs — a dashboard that ran the command
# itself would spend minutes of a suite on every poll, and would run it against whatever the
# worktree holds mid-step. Asked as behaviour rather than as "no subprocess": the run's spec
# names a test command whose execution leaves a trace on disk, its leaf log carries a Bash
# call of exactly that command, and after tests_json has answered, the trace is not there.
# The answer itself is checked too, so a marker missing because the endpoint raised before it
# ever looked at the command is a failure of this case and not a pass.
name="tests_json reads the run's test command and never executes it, so a command that would leave a trace leaves none"
problems=()
tnoexec_repo="$(repo testsnoexec)"
tnoexec_marker="$work/tests-noexec-trace"
tnoexec_cmd="sh -c 'echo executed > $tnoexec_marker'"
rm -f "$tnoexec_marker"

tnoexec_run="$(fabricate_run "$tnoexec_repo" 53 tdd/53-lamps-hum)"
fabricate_plan "$tnoexec_run" 53 "lamps hum" "a lamp hums" "$tnoexec_cmd"
cat > "$tnoexec_run/.tdd/develop-red.out" <<EOF
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "$tnoexec_cmd", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_1", "type": "tool_result", "content": "----\n3 passed, 0 failed", "is_error": false}]}}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$tnoexec_repo" tests_json "$work/tests-noexec.err" \
    '{"issue": ["53"]}' "$work/tests-noexec-53.json"
  if [[ ! -f "$work/tests-noexec-53.json" ]]; then
    problems+=("calling $module.tests_json wrote nothing: $(tail -n 1 "$work/tests-noexec.err")")
  else
    add_problems < <(python3 -c "$tests_runs"'
if len(runs) != 1 or runs[0].get("command") != sys.argv[3]:
    print("tests_json for issue 53 returned %s; want the one leaf test run of its own test "
          "command, %r — the marker below says nothing if the endpoint never read it"
          % (json.dumps(got, sort_keys=True)[:400], sys.argv[3]))
' "$work/tests-noexec-53.json" 53 "$tnoexec_cmd")
    if [[ -e "$tnoexec_marker" ]]; then
      problems+=("the run's test command left $(printf '%q' "$tnoexec_marker") behind, so tests_json executed $(printf '%q' "$tnoexec_cmd") instead of only reading it out of the spec and matching it in the leaf log")
    fi
  fi
fi

report "$name"

# --- the Tests endpoint counts `test-run` marks, not leaf Bash calls ---
# Since #342 every test-command run goes through `timed-test-run.sh <tier> <suites> <cmd>`,
# which is also what appends the `test-run` line to `.tdd/events.jsonl`. So a leaf no longer
# types its test command as a bare Bash call, the string match against the spec's `Test
# command:` line never held, and the pane was empty on a live run that had already run its
# suite seven times (#383). The mark is the thing to count: one entry per `test-run` line of
# the selected run's event log.
#
# The fixture makes the two rules disagree on purpose — three marks in the event log, and one
# leaf Bash call whose command is exactly the spec's `make test`. An endpoint counting Bash
# calls answers one; an endpoint counting marks answers three.
name="tests_json lists one entry per test-run mark in the run's event log, not per leaf Bash call matching the spec's command"
problems=()
tmarks_repo="$(repo testsmarks)"

tmarks_run="$(fabricate_run "$tmarks_repo" 54 tdd/54-lamps-buzz)"
fabricate_plan "$tmarks_run" 54 "lamps buzz" "a lamp buzzes"
fabricate_marks "$tmarks_run" 54 "a lamp buzzes" \
  skills/tdd/scripts/tests/lamp.test.sh skills/tdd/scripts/tests/lamp.test.sh
cat > "$tmarks_run/.tdd/develop-red.out" <<'EOF'
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_1", "type": "tool_result", "content": "----\n4 passed, 0 failed", "is_error": false}]}}
EOF

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$tmarks_repo" tests_json "$work/tests-marks.err" \
    '{"issue": ["54"]}' "$work/tests-marks-54.json"
  if [[ ! -f "$work/tests-marks-54.json" ]]; then
    problems+=("calling $module.tests_json wrote nothing: $(tail -n 1 "$work/tests-marks.err")")
  else
    add_problems < <(python3 -c "$tests_runs"'
if len(runs) != 3:
    print("tests_json for issue 54 returned %d test runs, %s; want one per `test-run` mark "
          "in that run’s event log, 3 — not the 1 bare `make test` Bash call in its leaf log"
          % (len(runs), json.dumps(runs, sort_keys=True)[:400]))
' "$work/tests-marks-54.json" 54)
  fi
fi

report "$name"

# --- each Tests entry names the suites its run covered and whether it passed ---
# Counting the marks is half the pane: a reader watching a run wants to know WHICH suites a
# test run covered and whether it came back green. Both are on the mark already — `suites` is
# the list timed-test-run.sh was handed (empty for a whole-suite tier), and `status` is the
# test command's own exit status, recorded since this issue's first step. So each entry names
# the suites its mark carries and says whether that status was success.
#
# The fixture's three marks disagree on both axes on purpose: one whole-suite run that passed,
# one named-suite run that failed, one named-suite run that passed. An endpoint handing back
# the same fields for all three — or none of them — is not answering "which suites, and did it
# pass".
name="tests_json entries name the suites their test-run mark covered and whether that run passed"
problems=()
tfields_repo="$(repo testsfields)"

tfields_run="$(fabricate_run "$tfields_repo" 56 tdd/56-lamps-gutter)"
fabricate_plan "$tfields_run" 56 "lamps gutter" "a lamp gutters"
fabricate_marks "$tfields_run" 56 "a lamp gutters" \
  skills/tdd/scripts/tests/gutter.test.sh skills/tdd/scripts/tests/flicker.test.sh

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$tfields_repo" tests_json "$work/tests-fields.err" \
    '{"issue": ["56"]}' "$work/tests-fields-56.json"
  if [[ ! -f "$work/tests-fields-56.json" ]]; then
    problems+=("calling $module.tests_json wrote nothing: $(tail -n 1 "$work/tests-fields.err")")
  else
    add_problems < <(python3 -c "$tests_runs"'
want = [{"suites": "", "passed": True},
        {"suites": "skills/tdd/scripts/tests/gutter.test.sh", "passed": False},
        {"suites": "skills/tdd/scripts/tests/flicker.test.sh", "passed": True}]
got = [{"suites": r.get("suites"), "passed": r.get("passed")} for r in runs]
if got != want:
    print("tests_json for issue 56 returned %s; want each entry to name the suites its "
          "`test-run` mark covered and whether that run passed: %s"
          % (json.dumps(got, sort_keys=True)[:400], json.dumps(want, sort_keys=True)))
' "$work/tests-fields-56.json" 56)
  fi
fi

report "$name"

# --- a run with no `test-run` mark is the empty list, and never another run's marks ---
# The other end of the rule the two cases above pin. What the pane lists is one entry per
# `test-run` mark in THE SELECTED RUN's own event log, so a run whose log holds none has no
# test run to report — the empty list, not the bare Bash calls its leaves happen to have
# typed, and not the marks of the run next door. A run predating #342 is the honest case of
# the first: its leaves ran the suite and nothing recorded it, and a pane that guessed from
# a matching Bash call would be reporting a number it cannot stand behind.
#
# The fixture puts both wrong answers within reach at once. The selected run, 57, has an
# event log carrying no `test-run` line and a leaf log holding a bare `make test` Bash call
# whose command is exactly its spec's; the run beside it, 58, carries three `test-run` marks.
# An endpoint falling back to leaf logs answers 1, one reading every run's log answers 3, and
# only one reading the selected run's marks alone answers 0.
name="tests_json answers the empty list for a run whose event log holds no test-run mark, and never another run's marks"
problems=()
tempty_repo="$(repo testsempty)"

tempty_sel="$(fabricate_run "$tempty_repo" 57 tdd/57-lamps-sputter)"
fabricate_plan "$tempty_sel" 57 "lamps sputter" "a lamp sputters"
cat > "$tempty_sel/.tdd/events.jsonl" <<'EOF'
{"ts": 1789910000, "issue": "57", "actor": "conductor", "phase": "", "step": "a lamp sputters", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": 1789910060, "issue": "57", "actor": "conductor", "phase": "develop-red", "step": "a lamp sputters", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
EOF
cat > "$tempty_sel/.tdd/develop-red.out" <<'EOF'
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_1", "type": "tool_result", "content": "----\n5 passed, 0 failed", "is_error": false}]}}
EOF

tempty_other="$(fabricate_run "$tempty_repo" 58 tdd/58-lamps-glare)"
fabricate_plan "$tempty_other" 58 "lamps glare" "a lamp glares"
fabricate_marks "$tempty_other" 58 "a lamp glares" \
  skills/tdd/scripts/tests/glare.test.sh skills/tdd/scripts/tests/glare.test.sh

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
else
  call_endpoint "$tempty_repo" tests_json "$work/tests-empty.err" \
    '{"issue": ["57"]}' "$work/tests-empty-57.json"
  if [[ ! -f "$work/tests-empty-57.json" ]]; then
    problems+=("calling $module.tests_json wrote nothing: $(tail -n 1 "$work/tests-empty.err")")
  else
    add_problems < <(python3 -c "$tests_runs"'
if runs:
    print("tests_json for issue 57 returned %d test runs, %s; want none — its own event log "
          "holds no `test-run` mark, so neither the bare `make test` Bash call in its leaf "
          "log nor run 58’s three marks are a test run of its own"
          % (len(runs), json.dumps(runs, sort_keys=True)[:400]))
' "$work/tests-empty-57.json" 57)
  fi
fi

report "$name"

# --- the Chatter endpoint's payload, asked of chatter_json directly: the current leaf's log ---
# The Chatter pane's contract — the rendered log of the leaf the selected run is CURRENTLY on
# — asked of the function that answers the endpoint rather than of a server answering it, the
# way the Tests and Events cases above ask theirs. Which leaf that is, is the run's own event
# log's answer: the newest `launch` event's `name`, which is the same leaf status.sh reports a
# run as being on (status.sh:79), and its log is `.tdd/<name>.out`. So the fixture run has two
# leaf logs and an event log whose newest launch names the second: an endpoint that handed back
# the first, or both, is not answering "the leaf it is currently on".
#
# What "rendered" means is render-leaf-log.sh's answer and not a second spelling of it, so the
# case renders the fixture with that script and compares — a case that spelled the renderer's
# rules again would pass a pane that rendered the log its own way.
name="chatter_json, called directly, returns the rendered log of the leaf the selected run is currently on"
problems=()
chat_repo="$(repo chatterdirect)"

chat_run="$(fabricate_run "$chat_repo" 54 tdd/54-lamps-buzz)"
cat > "$chat_run/.tdd/issue-54.md" <<'EOF'
# Plan for #54 — lamps buzz

- [x] a lamp buzzes
- [ ] a lamp stops buzzing
EOF
cat > "$chat_run/.tdd/develop-red.out" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s1", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Adding the case that pins the buzz."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_1", "type": "tool_result", "content": "FAIL - a lamp stops buzzing\n----\n4 passed, 1 failed", "is_error": true}]}}
EOF
cat > "$chat_run/.tdd/verify-green.out" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s2", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reading the diff against the spec."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_7", "name": "Bash", "input": {"command": "git diff HEAD~1", "description": "The step’s diff"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_7", "type": "tool_result", "content": "diff --git a/lamp.sh b/lamp.sh\n+  silence\n", "is_error": false}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "VERDICT: PASS"}]}}
EOF
chat_now="$(date +%s)"
cat > "$chat_run/.tdd/events.jsonl" <<EOF
{"ts": $((chat_now - 300)), "issue": "54", "actor": "conductor", "phase": "", "step": "a lamp stops buzzing", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((chat_now - 290)), "issue": "54", "actor": "developer", "phase": "red", "step": "a lamp stops buzzing", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red", "seq": 2}
{"ts": $((chat_now - 100)), "issue": "54", "actor": "verifier", "phase": "green", "step": "a lamp stops buzzing", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "verify-green", "seq": 3}
EOF

want_rendering "$chat_run/.tdd/verify-green.out" "$work/chatter-want.txt" "the fixture leaf log"

chatter_answer "$chat_repo" 54 chatter-direct
if [[ -n "$answer" ]]; then
  add_problems < <(python3 -c "$chatter_rendering"'
got, wanted = chatter(sys.argv[1], 54), want(sys.argv[2])
if got is not None and got != wanted:
    print("chatter_json for issue 54 returned %r; want render-leaf-log.sh’s rendering of "
          "verify-green.out, the leaf the run’s newest launch event names, which is %r"
          % (got[:400], wanted[:400]))
' "$answer" "$work/chatter-want.txt")
fi

report "$name"

# --- the Chatter endpoint on a verifier leaf: the log every leaf writes, not the duplicate ---
# Criterion 1 of #384. `.out` is a shell redirection the conductor types on a DEVELOPER leaf's
# launch line alone (SKILL.md:617); a verifier goes through verify.sh, whose outer redirect
# goes to /dev/null (SKILL.md:307), so no verify-*.out is ever written. What every leaf does
# get is supervise.sh's own capture of its combined output, `.tdd/<leaf>.log`
# (supervise.sh:211) — the same bytes the .out holds for the leaves that have both.
#
# So this fixture run is currently on a verifier, and that leaf's transcript is there as
# verify-red.log with no .out beside it: an endpoint that spells a leaf's transcript `.out`
# finds nothing and answers the empty string, which is the pane going blank for the whole
# verifier half of a run. What "rendered" means is render-leaf-log.sh's answer, as in the case
# above, so the case renders the fixture with that script and compares.
name="chatter_json returns the current verifier leaf's transcript, which is written as .log and never as .out"
problems=()
vlog_repo="$(repo chatterverifier)"

vlog_run="$(fabricate_run "$vlog_repo" 59 tdd/59-lamps-flare)"
cat > "$vlog_run/.tdd/issue-59.md" <<'EOF'
# Plan for #59 — lamps flare

- [ ] a lamp stops flaring
EOF
cat > "$vlog_run/.tdd/verify-red.log" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s3", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Reading the new case against the spec."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_5", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_5", "type": "tool_result", "content": "FAIL - a lamp stops flaring\n----\n9 passed, 1 failed", "is_error": true}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "VERDICT: PASS"}]}}
EOF
vlog_now="$(date +%s)"
cat > "$vlog_run/.tdd/events.jsonl" <<EOF
{"ts": $((vlog_now - 200)), "issue": "59", "actor": "conductor", "phase": "", "step": "a lamp stops flaring", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((vlog_now - 120)), "issue": "59", "actor": "verifier", "phase": "red", "step": "a lamp stops flaring", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "verify-red", "seq": 2}
EOF

want_rendering "$vlog_run/.tdd/verify-red.log" "$work/chatter-want-verify.txt" "the verifier leaf log"

chatter_answer "$vlog_repo" 59 chatter-verifier
if [[ -n "$answer" ]]; then
  add_problems < <(python3 -c "$chatter_rendering"'
got, wanted = chatter(sys.argv[1], 59), want(sys.argv[2])
if got is not None and got != wanted:
    blank = " — the empty string, which is what a run whose current leaf is a verifier gets " \
            "from a transcript spelled `.out`" if not got.strip() else ""
    print("chatter_json for issue 59 returned %r%s; want render-leaf-log.sh’s rendering of "
          "verify-red.log, the transcript of the verifier the run’s newest launch event "
          "names, which is %r" % (got[:400], blank, wanted[:400]))
' "$answer" "$work/chatter-want-verify.txt")
fi

report "$name"

# --- the Chatter endpoint on a closed leaf: the result text appended after the records ---
# Criterion 2 of #384. A leaf's transcript is records first and prose last: once the leaf
# closes, run-leaf.sh appends a blank line and then the plain-text result (run-leaf.sh:82-83).
# render-leaf-log.sh exits 2 on the first line that is not JSON and writes its accumulated
# output only after the loop (render-leaf-log.sh:33-46), so that tail throws away every line it
# had already rendered — and the pane goes blank the moment a leaf finishes, developer leaves
# included.
#
# The fixture has that shape: a run currently on develop-green whose transcript carries four
# stream-json records, then the blank line, then the result text. What the case asks for is
# that the records' own rendering — render-leaf-log.sh's answer for the records alone, as in
# the two cases above — is THERE in what the endpoint hands back, and not that the trailing
# prose is rendered one particular way: whether the fix relaxes the renderer's contract or
# stops handing it the tail is the solving run's call (#384), and both satisfy the criterion.
name="chatter_json renders a leaf transcript whose plain-text result is appended after its stream-json records"
problems=()
tail_repo="$(repo chattertail)"

tail_run="$(fabricate_run "$tail_repo" 61 tdd/61-lamps-flicker)"
cat > "$tail_run/.tdd/issue-61.md" <<'EOF'
# Plan for #61 — lamps flicker

- [ ] a lamp stops flickering
EOF
cat > "$work/chatter-tail-records.jsonl" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s4", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Making the flicker case pass."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_9", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_9", "type": "tool_result", "content": "10 passed, 0 failed", "is_error": false}]}}
EOF
{
  cat "$work/chatter-tail-records.jsonl"
  printf '\n'
  printf 'The step is green: 10 passed, 0 failed.\n'
} > "$tail_run/.tdd/develop-green.log"
tail_now="$(date +%s)"
cat > "$tail_run/.tdd/events.jsonl" <<EOF
{"ts": $((tail_now - 400)), "issue": "61", "actor": "conductor", "phase": "", "step": "a lamp stops flickering", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((tail_now - 150)), "issue": "61", "actor": "developer", "phase": "green", "step": "a lamp stops flickering", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green", "seq": 2}
EOF

want_rendering "$work/chatter-tail-records.jsonl" "$work/chatter-want-tail.txt" "the stream-json records"

chatter_answer "$tail_repo" 61 chatter-tail
if [[ -n "$answer" ]]; then
  add_problems < <(python3 -c "$chatter_rendering"'
got, wanted = chatter(sys.argv[1], 61), want(sys.argv[2])
if got is not None and wanted not in got:
    blank = " — the empty string, which is what a transcript with the result text appended " \
            "after its records gets from a renderer that exits 2 on the first line that is " \
            "not JSON" if not got.strip() else ""
    print("chatter_json for issue 61 returned %r%s; want an answer carrying "
          "render-leaf-log.sh’s rendering of develop-green.log’s stream-json records, "
          "which is %r" % (got[:400], blank, wanted[:400]))
' "$answer" "$work/chatter-want-tail.txt")
fi

report "$name"

# --- the Chatter endpoint with nothing to render: no leaf, and a leaf with no transcript ---
# Criterion 3 of #384. The two causes above are both about a transcript the pane failed to
# find or failed to render, and both fixes widen what it looks at: the log every leaf writes,
# and the records inside a log whose tail is prose. Neither may widen it into an answer where
# there is no transcript at all — the pane's own contract is that a run with nothing to show
# shows nothing, and an endpoint that answered with a placeholder, or with another leaf's log,
# or that raised on the missing file, would break that while satisfying both criteria above.
#
# The two shapes a run has nothing to show in, asked of one repository holding both: a run
# whose event log carries no `launch` at all, so status.sh's question "which leaf is it on"
# has no answer (#63), and a run whose newest launch names a leaf whose transcript is not
# there yet — neither `.log` nor `.out`, which is every leaf for the moment between the
# conductor's launch line and supervise.sh's first write (#65). Both answer the empty
# rendering, and the case says which of the two broke.
name="chatter_json answers the empty rendering for a run on no leaf and for a leaf that has written nothing yet"
problems=()
blank_repo="$(repo chatterblank)"

noleaf_run="$(fabricate_run "$blank_repo" 63 tdd/63-lamps-dim)"
cat > "$noleaf_run/.tdd/issue-63.md" <<'EOF'
# Plan for #63 — lamps dim

- [ ] a lamp stops dimming
EOF
noleaf_now="$(date +%s)"
cat > "$noleaf_run/.tdd/events.jsonl" <<EOF
{"ts": $((noleaf_now - 60)), "issue": "63", "actor": "conductor", "phase": "", "step": "a lamp stops dimming", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
EOF

nolog_run="$(fabricate_run "$blank_repo" 65 tdd/65-lamps-hum)"
cat > "$nolog_run/.tdd/issue-65.md" <<'EOF'
# Plan for #65 — lamps hum

- [ ] a lamp stops humming
EOF
nolog_now="$(date +%s)"
cat > "$nolog_run/.tdd/events.jsonl" <<EOF
{"ts": $((nolog_now - 90)), "issue": "65", "actor": "conductor", "phase": "", "step": "a lamp stops humming", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((nolog_now - 30)), "issue": "65", "actor": "developer", "phase": "red", "step": "a lamp stops humming", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red", "seq": 2}
EOF

chatter_answer "$blank_repo" 63 chatter-noleaf
noleaf_answer="$answer"
chatter_answer "$blank_repo" 65 chatter-nolog
nolog_answer="$answer"
if [[ -n "$noleaf_answer" && -n "$nolog_answer" ]]; then
  add_problems < <(python3 -c "$chatter_rendering"'
for issue, body, what in ((63, sys.argv[1], "whose event log names no launch, so it is on no leaf"),
                          (65, sys.argv[2], "on a leaf whose transcript is not there yet, as neither .log nor .out")):
    got = chatter(body, issue)
    if got is not None and got != "":
        print("chatter_json for issue %s, a run %s, returned %r; want the empty rendering"
              % (issue, what, got[:400]))
' "$noleaf_answer" "$nolog_answer")
fi

report "$name"

# --- the Chatter endpoint follows the run: a new current leaf switches what it returns ---
# The pane's other half of the contract: "the leaf the run is CURRENTLY on" is a question
# re-asked of the run on every poll, not one answered once. The case above pins WHICH leaf a
# static run is on; this one pins that the answer MOVES — the run launches a second leaf while
# the pane is polling, and the next answer is that leaf's log and not the first's. An endpoint
# that read the event log once, or that cached what it found there, answers the first case and
# not this one.
#
# Asked of chatter_json twice over one run whose event log grows between the two calls, which
# is what a run does: the conductor appends a `launch` line when it starts the next leaf. Both
# renderings come from render-leaf-log.sh, for the reason the case above gives, and they are
# also required to differ from each other — two identical fixtures would let an endpoint stuck
# on the first leaf pass.
name="chatter_json switches to the new leaf when the selected run's current leaf changes"
problems=()
switch_repo="$(repo chatterswitch)"

switch_run="$(fabricate_run "$switch_repo" 55 tdd/55-lamps-dim)"
cat > "$switch_run/.tdd/issue-55.md" <<'EOF'
# Plan for #55 — lamps dim

- [ ] a lamp dims
EOF
cat > "$switch_run/.tdd/develop-red.out" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s1", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Adding the case that pins the dimming."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_3", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_3", "type": "tool_result", "content": "FAIL - a lamp dims\n----\n7 passed, 1 failed", "is_error": true}]}}
EOF
cat > "$switch_run/.tdd/develop-green.out" <<'EOF'
{"type": "system", "subtype": "init", "session_id": "s2", "tools": ["Bash"]}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Making the dimming case pass."}]}}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_9", "name": "Bash", "input": {"command": "make test", "description": "Run the suite"}}]}}
{"type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_9", "type": "tool_result", "content": "----\n8 passed, 0 failed", "is_error": false}]}}
EOF
switch_now="$(date +%s)"
cat > "$switch_run/.tdd/events.jsonl" <<EOF
{"ts": $((switch_now - 400)), "issue": "55", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((switch_now - 390)), "issue": "55", "actor": "developer", "phase": "red", "step": "a lamp dims", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red", "seq": 2}
EOF

want_rendering "$switch_run/.tdd/develop-red.out" "$work/switch-want-red.txt" "the develop-red fixture"
want_rendering "$switch_run/.tdd/develop-green.out" "$work/switch-want-green.txt" "the develop-green fixture"

if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
elif [[ "${#problems[@]}" -eq 0 ]]; then
  call_endpoint "$switch_repo" chatter_json "$work/switch-first.err" \
    '{"issue": ["55"]}' "$work/switch-55-first.json"
  # The run moves on: the conductor's next leaf is launched, and the log says so.
  cat >> "$switch_run/.tdd/events.jsonl" <<EOF
{"ts": $((switch_now - 60)), "issue": "55", "actor": "developer", "phase": "green", "step": "a lamp dims", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green", "seq": 3}
EOF
  call_endpoint "$switch_repo" chatter_json "$work/switch-second.err" \
    '{"issue": ["55"]}' "$work/switch-55-second.json"
  if [[ ! -f "$work/switch-55-first.json" || ! -f "$work/switch-55-second.json" ]]; then
    problems+=("calling $module.chatter_json wrote nothing: $(tail -n 1 "$work/switch-first.err" "$work/switch-second.err" 2>/dev/null | tr '\n' ' ')")
  else
    add_problems < <(python3 -c "$chatter_rendering"'
first = chatter(sys.argv[1], 55, "before the second launch")
second = chatter(sys.argv[2], 55, "after the second launch")
want_red, want_green = want(sys.argv[3]), want(sys.argv[4])
if want_red == want_green:
    print("this case’s two leaf log fixtures render identically, so it could not tell an "
          "endpoint that switched leaves from one that did not")
if first is not None and first != want_red:
    print("chatter_json for issue 55 returned %r while its newest launch named develop-red; "
          "want render-leaf-log.sh’s rendering of develop-red.out, which is %r"
          % (first[:400], want_red[:400]))
if second is not None and second != want_green:
    stuck = " — it returned the log of the leaf it was on before that launch" if second == want_red else ""
    print("chatter_json for issue 55 returned %r after the run launched develop-green; want "
          "render-leaf-log.sh’s rendering of develop-green.out, the new current leaf, which "
          "is %r%s" % (second[:400], want_green[:400], stuck))
' "$work/switch-55-first.json" "$work/switch-55-second.json" \
  "$work/switch-want-red.txt" "$work/switch-want-green.txt")
  fi
fi

report "$name"

# --- the page on disk: one endpoint per pane, no server started ---
# The criterion is what the BROWSER does with the page, and nothing here is a browser: the
# suites depend on bash and python3 and nothing else (ci.yml). So it is asked of dashboard.html
# as it sits beside dashboard.sh rather than of a running server's answer (#330): the server hands the file out
# byte for byte with no per-request computation, so the file's own text is what the browser
# gets, and a server started only to read it back adds a process start and nothing else. Every
# pane's endpoint is fetched from a literal. A page that fetched an endpoint for no pane fails;
# a page whose three fetches sit behind one scheduler passes, since proving which fetch a timer
# reaches needs the engine this case lacks.
#
# What schedules the next fetch is the case below (#344), which took this one's timer half
# with it: this case demanded a setInterval at 2000 ms, and a page that fires on a fixed clock
# is the bug #344 fixes — the two cannot both be asked of one page.
name="dashboard.html, read off disk, fetches the Runs, Metrics and Events endpoints"
problems=()
disk_page="$scripts/dashboard.html"

fetches_endpoints Runs=/api/runs Metrics=/api/metrics Events=/api/events

report "$name"

# --- the page on disk: the next request is scheduled by the previous one answering ---
# The bug (#344) is an unbounded queue: a pane on a fixed clock issues a request every 2 s
# whether or not its last one has answered, so against a slow endpoint the requests pile up
# and no pane ever fills. The fix is that a pane schedules its next request only from the
# settlement of its previous one — both the resolve path and the reject path, since a pane
# whose fetch rejects and never reschedules is a pane that dies on the first hiccup — and so
# has at most one request in flight. Read off dashboard.html the way the case above reads it,
# for the same reason: nothing here is a browser.
#
# String literals and comments are blanked before anything is looked for, so a page whose
# own prose says "no setInterval" is not failed for its prose. A setTimeout counts as
# scheduled by an answer when it sits inside the argument list of a .then, .catch or .finally
# — which is the settlement handler the fetch promise calls — and the delay stays the 2000 ms
# the case above used to ask of setInterval.
name="dashboard.html, read off disk, schedules each pane's next request only from the previous one settling"
problems=()

ask_page '
import re
import sys

with open(sys.argv[1]) as f:
    page = f.read()

# The three quote characters JavaScript has, written as escapes: this program is passed to
# python inside single quotes, so the apostrophe cannot appear in it literally.
QUOTED = "\"\x27\x60"


# The page with the inside of every string literal and every comment replaced by spaces,
# every index unchanged. A call is then looked for in code only: a comment naming setInterval
# is prose, and the "/api/events?issue=" literal is a path, not a call.
def code_only(src):
    out = list(src)
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        pair = src[i:i + 2]
        if c in QUOTED:
            i += 1
            while i < n and src[i] != c:
                if src[i] == "\\":
                    out[i] = " "
                    i += 1
                if i < n:
                    out[i] = " "
                    i += 1
            i += 1
        elif pair == "//":
            while i < n and src[i] != "\n":
                out[i] = " "
                i += 1
        elif pair == "/*":
            while i < n and src[i:i + 2] != "*/":
                out[i] = " "
                i += 1
            out[i:i + 2] = "  "
            i += 2
        else:
            i += 1
    return "".join(out)


# The index just past the ")" that closes a call whose "(" is at src[i - 1], or -1 when the
# page has no such ")". A regex cannot be asked where a call ends: a callback passed to
# setTimeout carries parentheses and commas of its own, and only one at depth 0 counts.
def balanced(src, i):
    depth = 1
    while i < len(src):
        if src[i] in "([{":
            depth += 1
        elif src[i] in ")]}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


# The last top-level argument of an argument list — a setTimeout s delay.
def last_arg(args):
    depth, cut = 0, 0
    for j, c in enumerate(args):
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            cut = j + 1
    return args[cut:].strip()


code = code_only(page)


# Every call in code whose name matches <pattern>, as (match, end) — end being the index just
# past the ")" that closes it, or -1 when nothing does. The match carries the name that was
# found, which the settlement handlers below need and the timers do not.
def calls(pattern):
    for m in re.finditer(pattern + r"\s*\(", code):
        yield m, balanced(code, m.end())


# The call at <m> as it reads on the page rather than as code_only blanked it, flattened onto
# one line and cut to what fits a problem line: a message names what is written there, not the
# spaces this program put in its place.
def shown(m, end):
    text = page[m.start():end] if end > 0 else page[m.start():m.end()]
    return " ".join(text.split())[:120]


# No fixed clock anywhere on the page: one setInterval left behind is one pane still queueing
# requests against an endpoint that has not answered.
for m, end in calls(r"\bsetInterval"):
    print("the page calls %s, so a pane fires on a fixed clock rather than on its previous "
          "request answering" % shown(m, end))

# Where a settlement handler body is: the argument list of .then, .catch or .finally.
spans = []
for m, end in calls(r"\.(then|catch|finally)"):
    if end > 0:
        spans.append((m.group(1), m.end(), end - 1))

timers = list(calls(r"\bsetTimeout"))
if not timers:
    print("the page calls setTimeout nowhere, so no pane schedules its next request from its "
          "previous one settling")
else:
    resolve = reject = False
    for m, end in timers:
        kinds = [kind for kind, a, b in spans if a <= m.start() < b]
        text = shown(m, end)
        if not kinds:
            print("the page calls %s outside every .then, .catch and .finally body, so that "
                  "request is not scheduled by the previous one settling" % text)
        if [k for k in kinds if k in ("then", "finally")]:
            resolve = True
        if [k for k in kinds if k in ("catch", "finally")]:
            reject = True
        delay = last_arg(code[m.end():end - 1]) if end > 0 else ""
        if delay != "2000":
            print("the page reschedules with %s, %s ms after the previous request settled; "
                  "want 2000" % (text, delay))
    if not resolve:
        print("no setTimeout on the page sits in a .then or .finally body, so a pane whose "
              "request resolves never asks again")
    if not reject:
        print("no setTimeout on the page sits in a .catch or .finally body, so a pane whose "
              "request rejects never asks again")
'

report "$name"

# --- the page on disk: a pane apiece for the Tests and Chatter endpoints ---
# The two endpoints the page does not yet poll. Asked of dashboard.html as it sits beside
# dashboard.sh, the way the two cases above ask theirs and for the same reason: nothing here
# is a browser, and the server hands the file out byte for byte with no per-request
# computation, so the file's own text is what a browser gets.
#
# Each of the two panes has an endpoint of its own, fetched from a literal — an endpoint
# named only in a comment or in the prose of a heading is not a poll. What schedules that
# fetch is the settlement case above, which is asked of the whole page rather than of one
# pane: it fails on a setInterval anywhere on the page and on any setTimeout outside a
# .then, .catch or .finally body, so a Tests or Chatter pane put on a fixed clock of its own
# reddens it. Proving which fetch a given timer reaches needs the engine these cases lack,
# which is why the scheduling half is not re-asked here pane by pane.
name="dashboard.html, read off disk, gives the Tests and Chatter panes an endpoint apiece to poll"
problems=()

fetches_endpoints Tests=/api/tests Chatter=/api/chatter

report "$name"

# --- the page served at / is dashboard.html, so the poll checks above are the served page's ---
# Before #330 the poll contract was asked of the page a running server handed out, so a server
# serving any other HTML failed it; the case above asks it of the file instead, and the first
# case only asks that / is some HTML. This ties the two back together without a third server
# start: the body the start with no argument answered at / is compared with dashboard.html's
# own text, and any difference means the checks above were made of a page no browser gets.
# Both sides lose their trailing newlines to a command substitution, and nothing else.
name="the page dashboard.sh serves at / is dashboard.html, byte for byte"
problems=()
if [[ "$(http_status "${page:-}")" != 200 ]]; then
  problems+=("the start with no argument never answered 200 at http://127.0.0.1:$PORT/, so there is no served page to compare with dashboard.html")
elif [[ ! -f "$disk_page" ]]; then
  problems+=("there is no dashboard.html beside dashboard.sh to compare the served page with")
else
  served_page="$(http_body "$page")"
  file_page="$(cat "$disk_page")"
  if [[ "$served_page" != "$file_page" ]]; then
    problems+=("GET / served $(printf '%q' "${served_page:0:200}")")
    problems+=("dashboard.html holds $(printf '%q' "${file_page:0:200}")")
  fi
fi

report "$name"

# --- a slow /api/runs must not starve /api/events: ordering, not elapsed time ---
# The one fact only a live process can answer about concurrency: while one request is still
# inside status.sh, another request to a different endpoint gets its answer. Asked by
# ordering — the Events answer arrives, and only afterwards does this case release the
# blocked Runs request — so nothing here is timed and no threshold in seconds is asserted.
#
# The server is started from a directory of symlinks to dashboard.sh, its python module and
# the page, beside a `status.sh` that is a stub blocking on a marker file. It has to be:
# dashboard.sh hands the server the `status.sh` sitting beside itself, so the only way to
# have a Runs request that is still computing when the Events request is made is a scripts
# directory whose status.sh is the stub. That is also why the shim at the top of the suite
# does not count this start — its argv names a .py under $work, not under $scripts.
name="/api/events answers while an /api/runs request is still blocked inside status.sh"
problems=()
slow_repo="$(repo slowruns)"
slow_run="$(fabricate_run "$slow_repo" 77 tdd/77-a-kettle-boils)"
cat > "$slow_run/.tdd/issue-77.md" <<'EOF'
# Plan for #77 — a kettle boils

- [ ] a kettle boils
EOF
cat > "$slow_run/.tdd/events.jsonl" <<'EOF'
{"ts": 1, "issue": "77", "actor": "conductor", "phase": "", "step": "a kettle boils", "event": "step-start", "attempt": "", "skill_commit": "abc"}
EOF
slow_log="$work/slowruns.log"
slow_entered="$work/slow-status-entered"
slow_release="$work/slow-status-release"
slow_settled="$work/slow-runs-settled"
slow_dir="$work/slow-scripts"
mkdir -p "$slow_dir"
cat > "$slow_dir/status.sh" <<EOF
#!/bin/sh
# The slow endpoint, stopped at a marker rather than at a duration: it says it has been
# entered, waits for the case to let it go, and only then answers the empty document.
: > '$slow_entered'
while [ ! -e '$slow_release' ]; do sleep 0.05; done
printf '{"runs": []}\n'
EOF
chmod +x "$slow_dir/status.sh"
slow_port="$(free_port)"

problem="$(port_problem "$slow_port")"
if [[ -n "$module_problem" ]]; then
  problems+=("$module_problem")
elif [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  ln -s "$scripts/dashboard.sh" "$slow_dir/dashboard.sh"
  ln -s "$scripts/$module.py" "$slow_dir/$module.py"
  ln -s "$scripts/dashboard.html" "$slow_dir/dashboard.html"
  ln -s "$METRICS" "$slow_dir/metrics.sh"

  launch "$slow_dir/dashboard.sh" "$slow_repo" "$slow_log" "$slow_port"
  slow_pid=$!

  # The three URLs this case fetches are three paths on one server, so its address is
  # spelled once: the page it waits to come up, the Runs request that blocks, and the Events
  # request that has to be answered while it does.
  slow_base="http://127.0.0.1:$slow_port"
  slow_url="$slow_base/"
  slow_page="$(serve_until_up "$slow_url")"
  problem="$(answer_problem "$slow_url" "$slow_log" "$slow_page")"
  if [[ -n "$problem" ]]; then
    problems+=("$problem")
  else
    # The Runs request, in the background, and the wait is for the stub to say it has been
    # entered — not for a number of seconds — so what follows happens with that request
    # provably still inside status.sh.
    # The marker is written only where the fetch came back with an answer, so `slow_settled`
    # means the server answered the Runs request and never that the client gave up on it.
    (fetch "$slow_base/api/runs" >/dev/null 2>&1 && : > "$slow_settled") &
    slow_runs_pid=$!
    slow_i=0
    while [[ ! -e "$slow_entered" && "$slow_i" -lt 100 ]]; do
      sleep 0.1
      slow_i=$((slow_i + 1))
    done

    if [[ ! -e "$slow_entered" ]]; then
      problems+=("the /api/runs request never reached status.sh, so nothing was blocking when /api/events was asked; the server left: $(printf '%q' "$(cat "$slow_log" 2>/dev/null)")")
    else
      events_url="$slow_base/api/events?issue=77"
      events_answer="$(fetch "$events_url" 2>/dev/null || :)"
      # Read before the stub is released: an /api/runs that had already answered would mean
      # the two were never in flight together, whatever the Events answer was.
      [[ -e "$slow_settled" ]] && slow_runs_settled=1 || slow_runs_settled=""

      if [[ -z "$events_answer" ]]; then
        problems+=("GET $events_url got no answer while an /api/runs request was blocked inside status.sh, so the slow endpoint starves the cheap one")
      elif [[ "$(http_status "$events_answer")" != 200 ]]; then
        problems+=("GET $events_url answered $(http_status "$events_answer") while /api/runs was blocked, want 200")
      elif [[ "$(http_body "$events_answer")" != *step-start* ]]; then
        problems+=("GET $events_url answered while /api/runs was blocked, but without run #77's events: $(printf '%q' "$(http_body "$events_answer")")")
      fi
      [[ -z "$slow_runs_settled" ]] ||
        problems+=("the blocked /api/runs request had already answered before /api/events was asked, so the two were never in flight together")
    fi

    : > "$slow_release"
    wait "$slow_runs_pid" 2>/dev/null
  fi

  stop "$slow_pid"
fi

report "$name"

# --- the whole suite starts at most two servers ---
# Last on purpose: it reads the count every case above left on $starts, through the shim
# installed at the top (#330). Only the lifecycle facts — the default port, a port argument,
# loopback only, exit 0 on SIGINT, one process answering more than once — need a process;
# every payload and the page's own text are asked of a function or a file. A count of zero
# is the shim not counting, not a suite that started nothing, and fails as that.
name="the dashboard suite starts at most 2 dashboard.sh servers, counted at python3's exec"
problems=()
server_starts="$(wc -l < "$starts" | tr -d ' ')"
if [[ "$server_starts" -eq 0 ]]; then
  problems+=("the python3 shim counted no server start at all, so it is not counting what dashboard.sh execs")
elif [[ "$server_starts" -gt 2 ]]; then
  problems+=("$server_starts dashboard.sh servers were started across the suite, want at most 2; each start's python3 argv:")
  while IFS= read -r line; do
    problems+=("  $line")
  done < "$starts"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

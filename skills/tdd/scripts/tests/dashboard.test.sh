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
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

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

# launch <repo> <log> [port] — start dashboard.sh in the background from <repo>, its output
# on <log>, and leave its pid in `$!` for the caller to interrupt and wait on. `exec` inside
# the subshell so that pid is the server's own and not a shell wrapping it — the SIGINT has
# to reach the thing that is serving. PYTHONPATH cleared and PYTHONNOUSERSITE set so an
# importable package in the caller's environment cannot be what makes it work: "stdlib-only"
# is part of the criterion, and a server that needed a third-party module would have it to
# hand otherwise. Started here rather than in a command substitution because a pid the
# calling shell is not the parent of cannot be `wait`ed on, and the exit status after SIGINT
# is half of what the first case asks.
launch() {  # launch <repo> <log> [port]
  local dir="$1" out="$2"
  shift 2
  (cd "$dir" && PYTHONPATH= PYTHONNOUSERSITE=1 exec "$DASH" "$@" >"$out" 2>&1) &
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

# fetch_endpoint <repo> <tag> <path> <bodyfile> — start dashboard.sh in <repo> on a port the
# kernel says is free, GET <path> from it, leave the response body on <bodyfile>, and stop the
# server again; print the reason there is no body to assert on, or nothing. Every endpoint
# case below is that shape and differs only in the run fixtures it fabricates and in what it
# then asks of the body, so the scaffolding between the two is written once here. The port is
# asked of the kernel per case rather than being the default, so a case is never answered by
# another case's server.
fetch_endpoint() {  # fetch_endpoint <repo> <tag> <path> <bodyfile>
  local dir="$1" log="$work/$2.log" path="$3" out="$4"
  local port url answer problem pid
  port="$(free_port)"
  problem="$(port_problem "$port")"
  if [[ -n "$problem" ]]; then
    echo "$problem"
    return
  fi
  launch "$dir" "$log" "$port"
  pid=$!
  url="http://127.0.0.1:$port$path"
  answer="$(serve_until_up "$url")"
  problem="$(answer_problem "$url" "$log" "$answer")"
  if [[ -n "$problem" ]]; then
    echo "$problem"
  else
    http_body "$answer" > "$out"
  fi
  stop "$pid" || :
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

# --- no argument: the page at / on the default port, and exit 0 on SIGINT ---
name="dashboard.sh with no argument serves the page at / on port 8765 and exits 0 when sent SIGINT"
problems=()
served="$(repo served)"
log="$work/served.log"

problem="$(port_problem "$PORT")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch "$served" "$log"
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

# --- an argument: that port, and no interface but loopback ---
# Both halves of one criterion, asked of one running server: the page has to answer on the
# port the argument named (not the default), and the same port has to refuse a connection
# made to this machine's other address. Two servers could not answer the second question
# together — a second one on the same port would fail to bind — so it is one launch.
name="dashboard.sh with a port argument serves the page on that port and binds 127.0.0.1 only"
problems=()
arg_repo="$(repo argport)"
arg_log="$work/argport.log"
arg_port="$(free_port)"

problem="$(port_problem "$arg_port")"
if [[ -z "$problem" && "$arg_port" == "$PORT" ]]; then
  problem="the kernel handed out $arg_port, which is the default port: a server ignoring its argument would look right, so this case cannot run on it"
fi
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch "$arg_repo" "$arg_log" "$arg_port"
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

  stop "$arg_pid" || :
fi

report "$name"

# --- the Runs endpoint: what status.sh --json returns ---
# The pane is a reader of a script that already exists, so the criterion is an equality and
# not a shape: whatever `status.sh --json` says of the repository the server was started
# from, GET /api/runs has to say too. Asking it that way means no field of that document is
# spelled twice — a run's issue, title, branch, step, phase, actor, cost and state, and the
# scope object beside them — so the case cannot drift from status.sh as status.sh grows.
#
# One fabricated run so the answer is not the empty one: a ledger of two steps with the first
# ticked, and an event log whose newest events are seconds old, so both readings agree the run
# is running rather than one of them calling it stale.
#
# `elapsed_seconds` is the one field that cannot be equal: it is `now` minus the leaf's launch
# timestamp, measured once when the endpoint answers and again when this case runs status.sh
# itself, so it counts the gap between the two calls. It is compared as a number seconds apart
# rather than dropped, because dropping it would let an endpoint that never reports elapsed
# time at all pass.
name="the Runs endpoint returns what status.sh --json returns"
problems=()
runs_repo="$(repo runsendpoint)"
runs_run="$(fabricate_run "$runs_repo" 21 tdd/21-lamps-glow)"
cat > "$runs_run/.tdd/issue-21.md" <<'EOF'
# Plan for #21 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
now="$(date +%s)"
cat > "$runs_run/.tdd/events.jsonl" <<EOF
{"ts": $((now - 120)), "issue": "21", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((now - 110)), "issue": "21", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((now - 60)), "issue": "21", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "0.25", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500"}
EOF
problem="$(fetch_endpoint "$runs_repo" runsendpoint /api/runs "$work/runs-endpoint.json")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  # status.sh's own answer to the same question, asked from the same repository and with
  # the same environment the launch gave the server, so any difference is the endpoint's.
  (cd "$runs_repo" && PYTHONPATH= PYTHONNOUSERSITE=1 "$STATUS" --json) \
    > "$work/runs-status.json" 2>/dev/null
  while IFS= read -r line; do
    [[ -n "$line" ]] && problems+=("$line")
  done < <(python3 -c '
import json, sys


def load(path):
    with open(path) as f:
        return json.load(f)


try:
    got = load(sys.argv[1])
except ValueError:
    with open(sys.argv[1]) as f:
        print("the endpoint body is not JSON; it starts: %r" % f.read()[:200])
    sys.exit()
want = load(sys.argv[2])
if not isinstance(got, dict):
    print("the endpoint returned a %s; status.sh --json returns an object"
          % type(got).__name__)
    sys.exit()


def without_elapsed(doc):
    out = json.loads(json.dumps(doc))
    for run in out.get("runs", []) if isinstance(out.get("runs"), list) else []:
        if isinstance(run, dict):
            run.pop("elapsed_seconds", None)
    return out


bare_got, bare_want = without_elapsed(got), without_elapsed(want)
if bare_got != bare_want:
    print("the endpoint returned %s" % json.dumps(bare_got, sort_keys=True))
    print("status.sh --json returns %s" % json.dumps(bare_want, sort_keys=True))
    sys.exit()
for i, (g, w) in enumerate(zip(got["runs"], want["runs"])):
    if "elapsed_seconds" not in g:
        print("run %d has no elapsed_seconds from the endpoint; status.sh --json "
              "reports %s" % (i, w.get("elapsed_seconds")))
    elif abs(int(g["elapsed_seconds"]) - int(w["elapsed_seconds"])) > 10:
        print("run %d elapsed_seconds is %s from the endpoint and %s from status.sh --json, "
              "more than the 10 s the two calls can be apart"
              % (i, g["elapsed_seconds"], w["elapsed_seconds"]))
' "$work/runs-endpoint.json" "$work/runs-status.json")
fi

report "$name"

# --- the Metrics endpoint: live for a running run, the committed report for a finished one ---
# The pane is a reader of metrics.sh and of the report the conductor commits beside the
# ledger (`.tdd/issue-<n>-metrics.md`, SKILL.md:858), so the criterion is two equalities over
# two runs: a run still going has its figures RECOMPUTED from `.tdd/events.jsonl`, and a run
# that ended has the committed file handed back verbatim — the account of the run as it was
# written, not a reading of a log that may since have been pushed and pruned.
#
# What makes the two distinguishable is that BOTH fabricated runs carry a committed report,
# and neither file is what metrics.sh would print for its log. So an endpoint that read the
# file for everything fails on the running run, and one that recomputed everything fails on
# the finished one; only the split the criterion names passes. metrics.sh reads the log and
# the ledger and asks no clock, so its live answer here is a stable string to compare with.
#
# `done`/`bail` is what ends a run — the mark status.sh already reads for its `state`
# (status.sh:76) — so the finished run's log carries a `done` and the running run's newest
# event is seconds old with no such mark.
name="the Metrics endpoint recomputes a running run and returns the committed report for a finished one"
problems=()
met_repo="$(repo metricsendpoint)"

# The running run: two steps, the first ticked, newest event seconds old, no `done`.
met_live="$(fabricate_run "$met_repo" 31 tdd/31-lamps-glow)"
cat > "$met_live/.tdd/issue-31.md" <<'EOF'
# Plan for #31 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
met_now="$(date +%s)"
cat > "$met_live/.tdd/events.jsonl" <<EOF
{"ts": $((met_now - 120)), "issue": "31", "actor": "conductor", "phase": "", "step": "a lamp glows", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((met_now - 110)), "issue": "31", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-red"}
{"ts": $((met_now - 60)), "issue": "31", "actor": "developer", "phase": "red", "step": "a lamp glows", "event": "usage", "attempt": "1", "skill_commit": "abc", "total_cost_usd": "0.25", "input_tokens": "1000", "output_tokens": "200", "cache_read_input_tokens": "3000", "cache_creation_input_tokens": "500", "num_turns": "7", "duration_api_ms": "12000"}
EOF
# A committed report the running run must NOT be answered with: the run is still spending, so
# a file written when the step before it ended is exactly the stale reading the criterion
# splits on. Its heading is one metrics.sh never prints, so the two can never be confused.
cat > "$met_live/.tdd/issue-31-metrics.md" <<'EOF'
# a stale committed report for #31 that metrics.sh would never print
EOF

# The finished run: a log that ends in `done`, and the committed report that is the answer.
met_done="$(fabricate_run "$met_repo" 32 tdd/32-lamps-dim)"
cat > "$met_done/.tdd/issue-32.md" <<'EOF'
# Plan for #32 — lamps dim

- [x] a lamp exists
- [x] a lamp dims
EOF
cat > "$met_done/.tdd/events.jsonl" <<EOF
{"ts": $((met_now - 9000)), "issue": "32", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((met_now - 8900)), "issue": "32", "actor": "developer", "phase": "green", "step": "a lamp dims", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green"}
{"ts": $((met_now - 8800)), "issue": "32", "actor": "verifier", "phase": "green", "step": "a lamp dims", "event": "verdict", "attempt": "1", "skill_commit": "abc", "verdict": "PASS"}
{"ts": $((met_now - 8700)), "issue": "32", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-done", "attempt": "", "skill_commit": "abc"}
{"ts": $((met_now - 8600)), "issue": "32", "actor": "conductor", "phase": "", "step": "", "event": "done", "attempt": "", "skill_commit": "abc", "pr": "https://example.invalid/pr/2"}
EOF
cat > "$met_done/.tdd/issue-32-metrics.md" <<'EOF'
# What solving #32 cost — the committed report, verbatim

| phase | attempts |
|---|---|
| green | 1 |
EOF

problem="$(fetch_endpoint "$met_repo" metricsendpoint /api/metrics "$work/metrics-endpoint.json")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  # metrics.sh's own answer for the running run, asked from that run's worktree the way
  # the conductor asks it, so a difference is the endpoint's and not the fixture's.
  (cd "$met_live" && PYTHONPATH= PYTHONNOUSERSITE=1 "$METRICS" 31) \
    > "$work/metrics-live.md" 2>/dev/null
  while IFS= read -r line; do
    [[ -n "$line" ]] && problems+=("$line")
  done < <(python3 -c '
import json, sys

body, live_path, committed_path = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(body) as f:
        got = json.load(f)
except ValueError:
    with open(body) as f:
        print("the endpoint body is not JSON; it starts: %r" % f.read()[:200])
    sys.exit()
if not isinstance(got, dict) or not isinstance(got.get("issues"), dict):
    print("the endpoint returned %s; want an object with an \"issues\" object keyed by "
          "issue number" % json.dumps(got, sort_keys=True)[:300])
    sys.exit()
issues = got["issues"]
if sorted(issues) != ["31", "32"]:
    print("the endpoint reports issues %s; want the two runs 31 and 32"
          % json.dumps(sorted(issues)))
    sys.exit()
with open(live_path) as f:
    live = f.read()
with open(committed_path) as f:
    committed = f.read()
if issues["31"] != live:
    print("issue 31 is running, so its report has to be recomputed from the event log: the "
          "endpoint returned %r, and metrics.sh 31 prints %r"
          % (issues["31"][:300], live[:300]))
if issues["32"] != committed:
    print("issue 32 ended with a done mark, so its report has to be the committed "
          ".tdd/issue-32-metrics.md: the endpoint returned %r, and the committed file holds "
          "%r" % (issues["32"][:300], committed[:300]))
' "$work/metrics-endpoint.json" "$work/metrics-live.md" "$met_done/.tdd/issue-32-metrics.md")
fi

report "$name"

# --- the Events endpoint: the selected run's log, newest last ---
# The pane is a reader of `.tdd/events.jsonl`, so the criterion is the log itself: the lines
# of the SELECTED run, parsed, in the order the file has them — which is oldest first and so
# newest last. Selected by issue number, because that is what names a run everywhere else the
# page already reads: `status.sh --json` keys each run object by `issue`, and the Metrics
# endpoint keys its `issues` object by the same number.
#
# Two fabricated runs, and only one of them asked for: an endpoint that returned every run's
# events, or the wrong run's, fails here rather than looking right against a lone fixture.
# The other run's log carries a mark no line of the selected one does, so the two can never
# be confused for one another.
#
# A "tail" is a suffix, and how long a one is the endpoint's to choose: the case asserts that
# what comes back IS a contiguous suffix of the log ending at its newest line, which is what
# "newest last" means and what a reversed answer breaks, and says nothing about how many
# lines a tail is. The log is thirty events so that both a cap shorter than it and no cap at
# all satisfy that, and neither is read as this step's business.
name="the Events endpoint returns the selected run's events.jsonl tail, newest last"
problems=()
ev_repo="$(repo eventsendpoint)"

ev_sel="$(fabricate_run "$ev_repo" 41 tdd/41-lamps-flicker)"
cat > "$ev_sel/.tdd/issue-41.md" <<'EOF'
# Plan for #41 — lamps flicker

- [x] a lamp exists
- [ ] a lamp flickers
EOF
ev_now="$(date +%s)"
: > "$ev_sel/.tdd/events.jsonl"
for i in $(seq 1 30); do
  printf '{"ts": %s, "issue": "41", "actor": "developer", "phase": "red", "step": "a lamp flickers", "event": "launch", "attempt": "%s", "skill_commit": "abc", "name": "develop-red", "seq": %s}\n' \
    "$((ev_now - 3000 + i * 10))" "$i" "$i" >> "$ev_sel/.tdd/events.jsonl"
done

# The run that must NOT be answered with. Its every line carries `"issue": "42"`, so a single
# line of it in the answer is visible as such.
ev_other="$(fabricate_run "$ev_repo" 42 tdd/42-lamps-dim)"
cat > "$ev_other/.tdd/issue-42.md" <<'EOF'
# Plan for #42 — lamps dim

- [ ] a lamp dims
EOF
cat > "$ev_other/.tdd/events.jsonl" <<EOF
{"ts": $((ev_now - 200)), "issue": "42", "actor": "conductor", "phase": "", "step": "a lamp dims", "event": "step-start", "attempt": "", "skill_commit": "abc", "seq": 1}
{"ts": $((ev_now - 100)), "issue": "42", "actor": "developer", "phase": "green", "step": "a lamp dims", "event": "launch", "attempt": "1", "skill_commit": "abc", "name": "develop-green", "seq": 2}
EOF

problem="$(fetch_endpoint "$ev_repo" eventsendpoint "/api/events?issue=41" \
  "$work/events-endpoint.json")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  while IFS= read -r line; do
    [[ -n "$line" ]] && problems+=("$line")
  done < <(python3 -c '
import json, sys

body, log_path = sys.argv[1], sys.argv[2]
try:
    with open(body) as f:
        got = json.load(f)
except ValueError:
    with open(body) as f:
        print("the endpoint body is not JSON; it starts: %r" % f.read()[:200])
    sys.exit()
if not isinstance(got, dict) or not isinstance(got.get("events"), list):
    print("the endpoint returned %s; want an object with an \"events\" array"
          % json.dumps(got, sort_keys=True)[:300])
    sys.exit()
events = got["events"]
with open(log_path) as f:
    want = [json.loads(raw) for raw in f if raw.strip()]
if not events:
    print("the endpoint returned no events; the selected run’s log has %d" % len(want))
    sys.exit()
if len(events) > len(want):
    print("the endpoint returned %d events; the selected run’s log has only %d"
          % (len(events), len(want)))
    sys.exit()
tail = want[len(want) - len(events):]
if events != tail:
    print("the endpoint returned %s" % json.dumps(events, sort_keys=True)[:400])
    print("the last %d lines of the run’s log, newest last, are %s"
          % (len(events), json.dumps(tail, sort_keys=True)[:400]))
' "$work/events-endpoint.json" "$ev_sel/.tdd/events.jsonl")
fi

report "$name"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

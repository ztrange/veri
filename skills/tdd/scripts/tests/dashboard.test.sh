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
runs_log="$work/runsendpoint.log"
runs_port="$(free_port)"

problem="$(port_problem "$runs_port")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch "$runs_repo" "$runs_log" "$runs_port"
  runs_pid=$!

  runs_url="http://127.0.0.1:$runs_port/api/runs"
  runs_answer="$(serve_until_up "$runs_url")"
  problem="$(answer_problem "$runs_url" "$runs_log" "$runs_answer")"

  if [[ -n "$problem" ]]; then
    problems+=("$problem")
  else
    http_body "$runs_answer" > "$work/runs-endpoint.json"
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

  stop "$runs_pid" || :
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

met_log="$work/metricsendpoint.log"
met_port="$(free_port)"

problem="$(port_problem "$met_port")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch "$met_repo" "$met_log" "$met_port"
  met_pid=$!

  met_url="http://127.0.0.1:$met_port/api/metrics"
  met_answer="$(serve_until_up "$met_url")"
  problem="$(answer_problem "$met_url" "$met_log" "$met_answer")"

  if [[ -n "$problem" ]]; then
    problems+=("$problem")
  else
    http_body "$met_answer" > "$work/metrics-endpoint.json"
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

  stop "$met_pid" || :
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

#!/usr/bin/env bash
# Unit tests for scripts/dashboard.sh — the local web dashboard over the run data status.sh
# and metrics.sh read.
#
# Contract under test:
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
# Run: scripts/tests/dashboard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
DASH="$HERE/../dashboard.sh"
STATUS="$HERE/../status.sh"
METRICS="$HERE/../metrics.sh"
scripts="$(cd "$HERE/.." && pwd)"

work="$(scratch_dir)"

PORT=8765

add_problems() {
  local line
  while IFS= read -r line; do
    [[ -n "$line" ]] && problems+=("$line")
  done
}

repo() {  # repo <name> -> path
  local dir="$work/$1"
  new_repo -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

fabricate_run() {  # fabricate_run <repo> <n> <branch> -> path
  local dir="$1/.tdd/wt/$2"
  new_repo -b "$3" "$dir" >/dev/null 2>&1
  mkdir -p "$dir/.tdd"
  echo "$dir"
}

reachable() {  # reachable <host> <port>
  python3 -c 'import socket, sys
s = socket.socket(); s.settimeout(1.0)
sys.exit(0 if s.connect_ex((sys.argv[1], int(sys.argv[2]))) == 0 else 1)' "$1" "$2"
}

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

free_port() {
  python3 -c 'import socket
s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()'
}

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

http_status() { sed -n 1p <<< "$1"; }
http_ctype()  { sed -n 2p <<< "$1"; }
http_body()   { sed -n '3,$p' <<< "$1"; }

answer_problem() {  # answer_problem <url> <log> <answer>
  local url="$1" log="$2" answer="$3" status
  if [[ -z "$answer" ]]; then
    echo "no answer from $url after 10 s; the server left: $(printf '%q' "$(cat "$log" 2>/dev/null)")"
    return
  fi
  status="$(http_status "$answer")"
  [[ "$status" == 200 ]] || echo "GET $url answered $status, want 200"
}

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

launch() {  # launch <dash> <repo> <log> [port]
  local dash="$1" dir="$2" out="$3"
  shift 3
  (cd "$dir" && PYTHONPATH= PYTHONNOUSERSITE=1 exec "$dash" "$@" >"$out" 2>&1) &
}

port_problem() {  # port_problem <port>
  if [[ -z "$1" ]]; then
    echo "could not get a free port from the kernel, so there was nothing to pass dashboard.sh"
  elif reachable 127.0.0.1 "$1"; then
    echo "port $1 was already in use before dashboard.sh was started, so nothing this case fetches would be its answer"
  fi
}

stop() {  # stop <pid>
  kill -INT "$1" 2>/dev/null
  wait "$1" 2>/dev/null
}

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

want_rendering() {  # want_rendering <fixture> <want> <what>
  "$HERE/../render-leaf-log.sh" < "$1" > "$2" 2>/dev/null ||
    problems+=("render-leaf-log.sh could not render $3, which this case compares against")
}

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

fabricate_marks() {  # fabricate_marks <run> <n> <step> <failed-suite> <passed-suite>
  local now; now="$(date +%s)"
  cat > "$1/.tdd/events.jsonl" <<EOF
{"ts": $((now - 300)), "issue": "$2", "actor": "conductor", "phase": "", "step": "$3", "event": "step-start", "attempt": "", "skill_commit": "abc"}
{"ts": $((now - 240)), "issue": "$2", "actor": "", "phase": "", "step": "$3", "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": "fast", "suites": "", "seconds": "3", "status": "0"}
{"ts": $((now - 180)), "issue": "$2", "actor": "", "phase": "", "step": "$3", "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": "affected", "suites": "$4", "seconds": "9", "status": "1"}
{"ts": $((now - 120)), "issue": "$2", "actor": "", "phase": "", "step": "$3", "event": "test-run", "attempt": "", "skill_commit": "abc", "tier": "target", "suites": "$5", "seconds": "8", "status": "0"}
EOF
}

finish

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

exec_line="$(grep -E '^exec python3 ' "$DASH" || :)"
module="$(sed -nE 's/^exec python3 .*"\$HERE\/([A-Za-z_][A-Za-z0-9_]*)\.py".*/\1/p' <<< "$exec_line")"
module_problem=""
[[ -n "$module" ]] ||
  module_problem="dashboard.sh execs no .py module beside it; its exec line is: $(printf '%q' "$exec_line")"
work="$(scratch_dir)"

starts="$work/server-starts.log"
: > "$starts"
mkdir -p "$work/shim"
cat > "$work/shim/python3" <<EOF
#!/bin/sh
case "\$1" in
  '$scripts/$module.py') printf '%s\n' "\$*" >> '$starts' ;;
esac
exec '$(command -v python3)' "\$@"
EOF
chmod +x "$work/shim/python3"
export PATH="$work/shim:$PATH"

PORT=8765

add_problems() {
  local line
  while IFS= read -r line; do
    [[ -n "$line" ]] && problems+=("$line")
  done
}

ask_page() {
  local program="$1"
  shift
  if [[ ! -f "$disk_page" ]]; then
    problems+=("there is no dashboard.html beside dashboard.sh to read")
  else
    add_problems < <(python3 -c "$program" "$disk_page" "$@")
  fi
}

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
    for want in "<html" "</html>"; do
      [[ "$body" == *"$want"* ]] ||
        problems+=("the body of GET / has no '$want'; it starts: $(printf '%q' "${body:0:200}")")
    done
  fi

  stop "$dash_pid" && int_code=0 || int_code=$?
  [[ "$int_code" -eq 0 ]] || problems+=("exited $int_code after SIGINT, want 0")
fi

report "$name"

name="make test runs this suite"
problems=()
root="$(cd "$HERE/../../../.." && pwd)"
roster="$(make --no-print-directory -n -C "$root" test 2>&1)"
if ! grep -q 'skills/tdd/scripts/tests/dashboard\.test\.sh' <<< "$roster"; then
  problems+=("make -n test in $root does not name skills/tdd/scripts/tests/dashboard.test.sh, so make test never runs this suite")
fi

report "$name"

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

  arg_url="http://127.0.0.1:$arg_port/"
  arg_page="$(serve_until_up "$arg_url")"
  problem="$(answer_problem "$arg_url" "$arg_log" "$arg_page")"
  [[ -z "$problem" ]] || problems+=("$problem")

  elsewhere="$(other_addr)"
  if [[ -z "$elsewhere" ]]; then
    problems+=("this machine has no non-loopback IPv4 address, so 'binds 127.0.0.1 only' could not be asked of it")
  elif reachable "$elsewhere" "$arg_port"; then
    problems+=("the server answered on $elsewhere:$arg_port as well, so it is bound to every interface; want 127.0.0.1 only")
  fi

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

name="metrics_json keys one entry per run directory by its own issue number and runs metrics.sh once for a live run"
problems=()
mown_repo="$(repo metricsown)"
mown_run="$(fabricate_run "$mown_repo" 7 tdd/7-lamps-glow)"
cat > "$mown_run/.tdd/issue-7.md" <<'EOF'
# Plan for #7 — lamps glow

- [x] a lamp exists
- [ ] a lamp glows
EOF
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

name="dashboard.html, read off disk, fetches the Runs, Metrics and Events endpoints"
problems=()
disk_page="$scripts/dashboard.html"

fetches_endpoints Runs=/api/runs Metrics=/api/metrics Events=/api/events

report "$name"

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

name="dashboard.html, read off disk, gives the Tests and Chatter panes an endpoint apiece to poll"
problems=()

fetches_endpoints Tests=/api/tests Chatter=/api/chatter

report "$name"

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
  mkdir "$slow_dir/lib"
  ln -s "$scripts"/lib/*.sh "$slow_dir/lib/"

  launch "$slow_dir/dashboard.sh" "$slow_repo" "$slow_log" "$slow_port"
  slow_pid=$!

  slow_base="http://127.0.0.1:$slow_port"
  slow_url="$slow_base/"
  slow_page="$(serve_until_up "$slow_url")"
  problem="$(answer_problem "$slow_url" "$slow_log" "$slow_page")"
  if [[ -n "$problem" ]]; then
    problems+=("$problem")
  else
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

finish

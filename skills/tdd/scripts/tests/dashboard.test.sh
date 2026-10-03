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
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  ln -s "$scripts/dashboard.sh" "$slow_dir/dashboard.sh"
  ln -s "$scripts/veri" "$slow_dir/veri"
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

name="dashboard.sh, run through a symlink to the skill directory and from another working directory, serves dashboard.html at / and status.sh --json's stdout at /api/runs"
problems=()
link_repo="$(repo linked)"
link_log="$work/linked.log"
ln -s "$(cd "$scripts/.." && pwd)" "$work/skill-link"
link_port="$(free_port)"

problem="$(port_problem "$link_port")"
if [[ -n "$problem" ]]; then
  problems+=("$problem")
else
  launch ../skill-link/scripts/dashboard.sh "$link_repo" "$link_log" "$link_port"
  link_pid=$!

  link_base="http://127.0.0.1:$link_port"
  link_page="$(serve_until_up "$link_base/")"
  problem="$(answer_problem "$link_base/" "$link_log" "$link_page")"
  if [[ -n "$problem" ]]; then
    problems+=("$problem")
  else
    link_served="$(http_body "$link_page")"
    link_file="$(cat "$scripts/dashboard.html")"
    [[ "$link_served" == "$link_file" ]] ||
      problems+=("GET / through the symlink served $(printf '%q' "${link_served:0:200}"); dashboard.html holds $(printf '%q' "${link_file:0:200}")")

    link_runs="$(fetch "$link_base/api/runs" 2>/dev/null || :)"
    link_status="$(cd "$link_repo" && PYTHONPATH= PYTHONNOUSERSITE=1 "$STATUS" --json 2>/dev/null)"
    if [[ "$(http_status "$link_runs")" != 200 ]]; then
      problems+=("GET $link_base/api/runs through the symlink answered '$(http_status "$link_runs")', want 200")
    elif [[ "$(http_body "$link_runs")" != "$link_status" ]]; then
      problems+=("GET /api/runs through the symlink answered $(printf '%q' "$(http_body "$link_runs")"); status.sh --json prints $(printf '%q' "$link_status")")
    fi
  fi

  stop "$link_pid" || :
fi

report "$name"

finish

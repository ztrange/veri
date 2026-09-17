#!/usr/bin/env bash
# Unit tests for scripts/dashboard.sh — the local web dashboard over the same run data
# status.sh and metrics.sh read. Run from a target repo, it starts a stdlib-only Python
# server on 127.0.0.1 that serves one static HTML page and a JSON endpoint per pane.
# Zero-dependency plain-shell asserts, same idiom as status.test.sh.
#
# Contract under test (issue #110), this suite's first case:
#   dashboard.sh            with no argument, bind port 8765 and serve the one HTML page
#                           at /; exit 0 when sent SIGINT.
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

# listening <port> — true when something already accepts a connection there. Asked BEFORE
# the server is launched, and it fails the case closed: with a stranger's server on 8765 the
# fetch below would succeed without dashboard.sh having bound anything, and a case that
# cannot tell the two apart must not report a pass.
listening() {
  python3 -c 'import socket, sys
s = socket.socket(); s.settimeout(0.5)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)' "$1"
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

# --- no argument: the page at / on the default port, and exit 0 on SIGINT ---
# The server is launched with `exec` in the subshell so the pid the case holds is the
# server's own and not a shell wrapping it — the SIGINT has to reach the thing that is
# serving. PYTHONPATH cleared and PYTHONNOUSERSITE set so an importable package in the
# caller's environment cannot be what makes it work: "stdlib-only" is part of the criterion,
# and a server that needed a third-party module would have it to hand otherwise.
name="dashboard.sh with no argument serves the page at / on port 8765 and exits 0 when sent SIGINT"
problems=()
served="$(repo served)"
log="$work/served.log"

if listening "$PORT"; then
  problems+=("port $PORT was already in use before dashboard.sh was started, so nothing this case fetches would be its answer")
else
  (cd "$served" && PYTHONPATH= PYTHONNOUSERSITE=1 exec "$DASH" >"$log" 2>&1) &
  dash_pid=$!

  # Up to 10 s for it to come up — generous because a cold python3 start is the slowest
  # thing here, and a poll that gave up early would report "no page" for a server that
  # was merely still starting.
  page="" ; i=0
  while [[ "$i" -lt 100 ]]; do
    if page="$(fetch "http://127.0.0.1:$PORT/" 2>/dev/null)"; then break; fi
    page=""
    sleep 0.1
    i=$((i + 1))
  done

  if [[ -z "$page" ]]; then
    problems+=("no answer from http://127.0.0.1:$PORT/ after 10 s; the server left: $(printf '%q' "$(cat "$log" 2>/dev/null)")")
  else
    status="$(sed -n 1p <<< "$page")"
    ctype="$(sed -n 2p <<< "$page")"
    body="$(sed -n '3,$p' <<< "$page")"
    [[ "$status" == 200 ]] || problems+=("GET / answered $status, want 200")
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
  kill -INT "$dash_pid" 2>/dev/null
  wait "$dash_pid" 2>/dev/null && int_code=0 || int_code=$?
  [[ "$int_code" -eq 0 ]] || problems+=("exited $int_code after SIGINT, want 0")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

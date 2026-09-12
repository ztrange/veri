#!/usr/bin/env bash
# Unit tests for the docs guard suite's own case filter — like hermetic-suites.test.sh and
# workflow-timeouts.test.sh this suite has no single script as its subject: its subject is
# another suite, docs/tests/build-guards.test.sh, and the only way to ask what that suite
# does with an environment variable is to run it as a child process.
# Zero-dependency plain-shell asserts, same idiom as workflow-timeouts.test.sh.
#
# Why this exists (issue #119): every developer and verifier leaf on a docs issue ran
# `make docs-test` one to three times, at ~140 s a run, because the target test and the
# full suite resolve to the same command — build-guards.test.sh builds a sandbox and a
# page per case, twenty-eight of them, and had no way to run one. The 140 s of silence is
# also what supervise.sh's heartbeat sees.
#
# Contract under test:
#   ONLY=<substring> docs/tests/build-guards.test.sh runs the cases whose name contains
#   <substring> and no others — so it exits 0, reports exactly those cases in its count
#   line, and comes back in seconds rather than in the minutes the whole suite takes.
#
# The pin lives here, under `make test`, rather than inside the suite it is about: `make
# test` is the command veri's own preflight detects and the only docs-or-otherwise gate CI
# runs (docs-check left CI on 2026-09-11), so a filter pinned here is defended on every
# push. It costs `make test` one sandboxed page build, ~4 s.
#
# Run: scripts/tests/docs-guard-filter.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
SUITE="$ROOT/docs/tests/build-guards.test.sh"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The case this asks for by name, and what the suite must then report. A fixture, not a
# claim about that case: any single case would do, and this is the cheapest — one sandbox
# and one build, no git history. Named once here so a rename over in build-guards.test.sh
# has one place to be followed.
# 'baseline builds' and not 'builds': the last case of that suite is "the committed page is
# the one this tree builds", so the shorter substring would match two cases and this would
# be asserting something else.
ONLY_CASE='baseline builds'
ONLY_COUNT='1 passed, 0 failed'

# The ceiling a filtered run has to come back inside. One sandboxed build is ~4 s and the
# unfiltered suite is ~140 s, so anything in between separates them; 30 s is far enough
# above the one build to survive a loaded machine and far enough below the whole suite that
# a run which quietly builds the other twenty-seven sandboxes cannot slip under it.
LIMIT=30

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# kill_tree <pid> — end that process and everything it started, the way supervise.sh:66
# does: TERM to the whole process group first, so the suite's own EXIT trap runs and takes
# its sandboxes with it, then KILL after a grace for a child that ignored it. Each signal
# goes to the group and falls back to the bare process, for a launch that never became a
# group leader.
kill_tree() {
  local pid="$1"
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep 0.4; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

# run_filtered <only> <out> — run the guard suite with ONLY=<only>, its output into <out>,
# under a deadline; prints "<exit code> <elapsed seconds>".
#
# The deadline is the whole point of running it this way rather than with $(...): the
# failure this case exists to catch is a suite that ignores ONLY and builds everything, and
# unbounded that failure costs 140 s every time `make test` runs while the filter is still
# missing. Killed at the ceiling it costs 30 s and reports a non-zero exit, which is a
# truthful red either way.
#
# Launched in its own process group (job-control monitor mode, as supervise.sh does) so the
# deadline reaches the python build the suite is inside and not just the shell wrapping it.
run_filtered() {
  local only="$1" out="$2" pid code start elapsed
  set -m
  ONLY="$only" "$SUITE" >"$out" 2>&1 &
  pid=$!
  set +m
  start=$SECONDS
  while kill -0 "$pid" 2>/dev/null; do
    if (( SECONDS - start >= LIMIT )); then
      kill_tree "$pid"
      break
    fi
    sleep 1
  done
  wait "$pid" && code=0 || code=$?
  elapsed=$((SECONDS - start))
  printf '%s %s\n' "$code" "$elapsed"
}

# 1. The contract above, and all three of its halves in one case, because no two of them
#    are worth anything apart. A suite that ignores ONLY and runs everything is green on
#    "exited 0"; one that runs the matching case and then the rest of them is green on
#    "reported 1 passed"; and a run that came back in two seconds having done nothing at
#    all is green on the clock. Only the three together say the filter ran that case, ran
#    no other, and skipped the twenty-seven builds it did not need.
name="ONLY='$ONLY_CASE' runs that one case of build-guards.test.sh and nothing else, in seconds"
problems=()
out="$WORK/filtered.txt"
read -r code elapsed <<< "$(run_filtered "$ONLY_CASE" "$out")"
report_text="$(cat "$out" 2>/dev/null)"
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from ONLY='$ONLY_CASE' $SUITE, got $code after ${elapsed}s")
[[ "$report_text" == *"$ONLY_COUNT"* ]] ||
  problems+=("want '$ONLY_COUNT' in its output — the matching case and no other; got: $(printf '%s' "$report_text" | tail -3 | tr '\n' '/')")
(( elapsed < LIMIT )) ||
  problems+=("want a filtered run back inside ${LIMIT}s, got ${elapsed}s — it built the cases it was not asked for")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

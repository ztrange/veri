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

# run_filtered <only> — run the guard suite with ONLY=<only> under a deadline, and set the
# three things a case then asks about: `code`, its exit status; `elapsed`, the seconds it
# took; and `report_text`, everything it printed. Publishing them as variables is the same
# protocol `report` already uses for `problems` — the caller reads them where it stands.
#
# It owns its scratch file rather than being handed one: where the output is parked is
# nobody's business but this function's, and a caller that passes a path and then has to
# remember to read that same path back is two halves that can get out of step. One path
# reused across calls is enough — the redirect truncates it, and each caller reads it before
# the next run overwrites it.
#
# The deadline is the whole point of running the suite as a background job rather than
# inline: the failure this case exists to catch is a suite that ignores ONLY and builds
# everything, and unbounded that failure costs 140 s every time `make test` runs while the
# filter is still missing. Killed at the ceiling it costs 30 s and reports a non-zero exit,
# which is a truthful red either way.
#
# Launched in its own process group (job-control monitor mode, as supervise.sh does) so the
# deadline reaches the python build the suite is inside and not just the shell wrapping it.
run_filtered() {
  local only="$1" pid start out="$WORK/run.txt"
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
  report_text="$(cat "$out" 2>/dev/null)"
}

# in_time <what kind of run> — the deadline probe both cases end on, appended to `problems`
# when the run hit the ceiling rather than coming back inside it.
#
# Both cases make that claim for the same reason, so the reason is written here once: a
# suite that ignored ONLY goes on to build the sandboxes it was not asked for, and is still
# building them when kill_tree reaches it. Spelled out per case it read as two probes with
# the consequence reworded, which invites the next case to reword it again.
#
# It reads `elapsed` where run_filtered left it, the way the probes around it read `code`
# and `report_text`, and appends to the caller's `problems` — both are the protocol this
# suite already runs on rather than anything this function introduces.
in_time() {
  (( elapsed < LIMIT )) ||
    problems+=("want a $1 run back inside ${LIMIT}s, got ${elapsed}s — it built cases nothing asked for")
}

# 1. The contract above, and all three of its halves in one case, because no two of them
#    are worth anything apart. A suite that ignores ONLY and runs everything is green on
#    "exited 0"; one that runs the matching case and then the rest of them is green on
#    "reported 1 passed"; and a run that came back in two seconds having done nothing at
#    all is green on the clock. Only the three together say the filter ran that case, ran
#    no other, and skipped the twenty-seven builds it did not need.
name="ONLY='$ONLY_CASE' runs that one case of build-guards.test.sh and nothing else, in seconds"
problems=()
run_filtered "$ONLY_CASE"
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from ONLY='$ONLY_CASE' $SUITE, got $code after ${elapsed}s")
[[ "$report_text" == *"$ONLY_COUNT"* ]] ||
  problems+=("want '$ONLY_COUNT' in its output — the matching case and no other; got: $(printf '%s' "$report_text" | tail -3 | tr '\n' '/')")
in_time filtered
report "$name"

# 2. A filter that matches nothing is the typo path, and it is the one case where a silent
#    green is actively dangerous: every case skips, nothing is asserted, and a suite that
#    ends `[[ $fail -eq 0 ]]` exits 0 — so a leaf that mistyped its ONLY reads "the guards
#    pass" off a run that guarded nothing. Exit 3 is the code every veri script uses for
#    "nothing to do" (CLAUDE.md: exit codes are the API), which the conductor already tells
#    apart from a real negative.
#
#    Three probes, for the three halves of the step: the code, the message that says which
#    filter found nothing, and the claim that it ran no case. The last is pinned twice over
#    because either half alone is cheap to fake — a run back inside the ceiling could still
#    have built one sandbox, and a "0 passed" line could still be printed by a run that
#    built all twenty-eight and skipped the counting. The message is matched
#    case-insensitively on "no case" plus the filter itself: the wording is the
#    implementer's, but it has to name what was asked for, or it cannot be acted on.
NO_MATCH='no-such-case-zzz'
name="ONLY='$NO_MATCH' matches no case: exit 3, says so, and runs nothing"
problems=()
run_filtered "$NO_MATCH"
lowered="$(printf '%s' "$report_text" | tr 'A-Z' 'a-z')"
[[ "$code" == 3 ]] ||
  problems+=("want exit 3 — nothing to do — from ONLY='$NO_MATCH' $SUITE, got $code after ${elapsed}s")
[[ "$lowered" == *"no case"* && "$report_text" == *"$NO_MATCH"* ]] ||
  problems+=("want it to say no case matched '$NO_MATCH'; got: $(printf '%s' "$report_text" | tail -3 | tr '\n' '/')")
printf '%s\n' "$report_text" | grep -Eq '[1-9][0-9]* passed' &&
  problems+=("want no case run at all; got a count claiming passes: $(printf '%s' "$report_text" | tail -1)")
in_time no-match
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

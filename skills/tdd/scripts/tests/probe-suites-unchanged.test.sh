#!/usr/bin/env bash
# Unit tests for metrics.test.sh and harvest-usage.test.sh together — that folding their
# probes into fewer python3 processes (issue #331) dropped none of what they check.
# Zero-dependency plain-shell asserts, same idiom as harvest-usage-launch.test.sh.
#
# The roster below is every case the two suites held before #331 touched them (the plan
# commit, afa502eb), copied by hand: CI's checkout is shallow, so the suite cannot read the
# old files out of history. Each suite is run twice against a copy of the scripts:
#   the real scripts        → green, on exactly as many cases as the roster lists.
#   a product that answers  → every roster case red, by name — so each is still there, still
#   nothing (exits 0, no      runs, and still has an assertion that a wrong product trips.
#   output)
#
# Run: scripts/tests/probe-suites-unchanged.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/.."
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# variant <dir> — a copy of every top-level script and the sourced library, so each suite's
# own `$HERE` still finds its product, plus the two suites under observation.
variant() {
  mkdir -p "$1/tests"
  cp "$SCRIPTS"/*.sh "$1/"
  cp -R "$SCRIPTS/lib" "$1/lib"
  cp "$HERE/metrics.test.sh" "$HERE/harvest-usage.test.sh" "$1/tests/"
}

# mute <dir> <script> — replace one product script in a variant with one that exits 0 and
# says nothing.
mute() {
  printf '#!/bin/sh\nexit 0\n' > "$1/$2"
  chmod +x "$1/$2"
}

metrics_cases=(
  "a two-phase log renders one row per phase with its attempts, PASS, REJECT and kills"
  "a two-step log renders a per-step section with each step's counts and stuck retries"
  "each step's row says the revise attempts and refactor transforms it used of their budgets, and whether the refactor loop stopped by budget"
  "the phase and step rows carry their wall and API seconds, and the report gives the issue wall from its first event to done"
  "every phase row, step row and the total carry their turns, four token counts and dollars, and a line says whether the conductor own cost is in them"
  "a step recovered after a REJECT puts its rejected attempts into its phase rework and nothing into waste"
  "a bailed step puts every attempt, PASS verdicts included, into its phase waste and nothing into rework"
  "the report says how many steps of the plan were done and how the run ended, naming a bail's classification and a landed run's PR"
  "a log of exactly one run that ended in a done mark renders its issue wall as a number, not unknown"
  "a steps-done figure no step mark in the log supplies says unknown, not zero"
  "a step that ended in a pin mark and no step-done mark counts as done in the steps-done figure"
  "a log with two pin marks and one step-done mark for three ledger steps reports 3 of 3 planned"
  "a log whose steps end only in step-done marks, with no pin mark, counts only those steps as done"
  "a log with a bail mark followed by a resume and a done reports the run as landed, naming the PR"
  "on a log with a bail, a resume and a done the issue wall runs from the last resume to the done mark"
  "on a resumed run the issue-wall sentence says the wall starts at the last resume, not at the log's first event"
  "a log with no resume walls the issue from its first event and takes its outcome from its single ending mark"
  "on a run with no resume the issue-wall sentence says the wall starts at the log's first event"
  "on a log with a bail, a resume and a done the counts, wall seconds and costs are summed over both runs"
  "a step whose verifier was relaunched for no verdict reports those relaunches as their own count, apart from its retries and revises"
  "a step whose triage found nothing structural and one that owes structural candidates each report their own stopped value"
)
harvest_cases=(
  "a finished leaf: the harvester appends one usage event carrying the wall ms, API ms, turns, four token counts and dollars from that leaf's closing stream-json result record"
  "a leaf whose log carries no closing result record: the harvester appends no usage event and says so on stderr, naming itself and the leaf"
  "a leaf name leaf-role.sh refuses: the harvester appends no usage event and exits 2, naming itself and the leaf on stderr"
)

# 1. The criterion: every case either suite held before #331 is still there and still passes
#    against the real scripts, and still goes red against a product that answers nothing.
#      → metrics.test.sh `21 passed, 0 failed` and harvest-usage.test.sh `3 passed, 0 failed`
#        on the real scripts; every roster name on a FAIL line once metrics.sh, respectively
#        harvest-usage.sh, is muted.
name="every metrics.test.sh and harvest-usage.test.sh case that passed before #331 still passes, and still goes red against a product that answers nothing"
problems=()

real="$tmp/real"
variant "$real"
muted="$tmp/muted"
variant "$muted"
mute "$muted" metrics.sh
mute "$muted" harvest-usage.sh

# check_suite <suite> <case>... — the green run's count line, then each roster name red.
check_suite() {
  local suite="$1" out want c
  shift
  want="$# passed, 0 failed"
  out="$("$real/tests/$suite" 2>/dev/null)"
  [[ "$(printf '%s\n' "$out" | tail -n 1)" == "$want" ]] ||
    problems+=("$suite on the real scripts: want '$want', got: $(printf '%q' "$(printf '%s\n' "$out" | tail -n 3)")")
  out="$("$muted/tests/$suite" 2>/dev/null)"
  for c in "$@"; do
    printf '%s\n' "$out" | grep -qxF "FAIL - $c" ||
      problems+=("$suite against a muted product: want a FAIL line for '$c', found none")
  done
}

check_suite metrics.test.sh "${metrics_cases[@]}"
check_suite harvest-usage.test.sh "${harvest_cases[@]}"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

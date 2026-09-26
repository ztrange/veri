#!/usr/bin/env bash
# parallel-conductors.sh — rung 3 of the scope ladder: run several issue-conductors at once
# over the solvable set, from the target repo's primary checkout (#102).
#
# VERI_PARALLEL is how many conductors run at once, default 1. N conductors are N concurrent
# `claude -p` sessions, billed as such, so a value that is not a whole number >= 1 — zero, a
# word, set-but-empty — is a misconfigured run, not a decision: a diagnostic on stderr and
# exit 2 before anything is launched, never a guess at how much to spend.
#
# Usage:   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
set -euo pipefail

parallel="${VERI_PARALLEL-1}"

if [[ ! "$parallel" =~ ^[0-9]+$ ]] || (( 10#$parallel < 1 )); then
  echo "parallel-conductors: VERI_PARALLEL must be a whole number >= 1: '$parallel'" >&2
  exit 2
fi

HERE="$(cd "$(dirname "$0")" && pwd)"

# The loop: while fewer than VERI_PARALLEL conductors are in flight — launched here and not yet
# seen to finish — select with solvable-issues.sh and launch the first printed issue that is not
# already in flight, in the background. Then wait for whichever in-flight conductor ends first and
# select again: a blocker only closes when a human merges, so the set is recomputed after every
# completion rather than cached. With nothing in flight and nothing left to launch, the loop ends
# with solvable-issues.sh's own status — exit 3 once nothing is left.
declare -A in_flight=()   # issue number -> pid of its supervise.sh
while :; do
  while (( ${#in_flight[@]} < 10#$parallel )); do
    solvable="$("$HERE/solvable-issues.sh")" && rc=0 || rc=$?
    (( rc == 0 )) || break
    n=""
    for candidate in $solvable; do
      [[ -n "${in_flight[$candidate]:-}" ]] || { n="$candidate"; break; }
    done
    [[ -n "$n" ]] || break
    "$HERE/supervise.sh" "conductor-$n" "$HERE/run-conductor.sh" "$n" > /dev/null &
    in_flight[$n]=$!
  done
  (( ${#in_flight[@]} > 0 )) || exit "${rc:-3}"
  wait -n || true
  for n in "${!in_flight[@]}"; do
    kill -0 "${in_flight[$n]}" 2>/dev/null || unset "in_flight[$n]"
  done
done

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

# The loop: select with solvable-issues.sh, launch the first printed issue, wait for its
# conductor to end, then select again — a blocker only closes when a human merges, so the set is
# recomputed after every completion rather than cached. The loop ends when solvable-issues.sh
# stops answering 0 — exit 3 once nothing is left — and `set -e` hands its status back as ours.
while :; do
  solvable="$("$HERE/solvable-issues.sh")"
  "$HERE/supervise.sh" "conductor-${solvable%%[[:space:]]*}" \
    "$HERE/run-conductor.sh" "${solvable%%[[:space:]]*}" > /dev/null
done

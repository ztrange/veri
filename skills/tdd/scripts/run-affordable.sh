#!/usr/bin/env bash
# run-affordable.sh — can this run still afford to finish (issue #453, part of #447)?
#
# Usage:   run-affordable.sh <steps-remaining>     # run from the run's worktree
#
# Projects the run's spend so far plus <steps-remaining> steps at the median step's cost
# against VERI_RUN_BUDGET. Exit 1 — the clean negative, a real answer — when the projection
# exceeds the ceiling, printing the four figures it decided on: spent, steps remaining, the
# median and the projection.
#
# Spend and step costs are read through `step-cost.sh --steps`, the one reader of the event
# log, and the ceiling through step-budget.sh, so its default and its refusal of a bad value
# live in one place.
set -euo pipefail

remaining="${1-}"
if [[ ! "$remaining" =~ ^[0-9]+$ ]]; then
  echo "usage: run-affordable.sh <steps-remaining> (a whole number): '$remaining'" >&2
  exit 2
fi

HERE="$(cd "$(dirname "$0")" && pwd)"

budgets="$("$HERE/step-budget.sh")"
ceiling="${budgets##*$'\n'}"

steps="$("$HERE/step-cost.sh" --steps)"

# hazard: bash arithmetic is integer and every figure is a decimal, so awk does the arithmetic.
sort -n <<< "$steps" | awk -v n="$remaining" -v ceiling="$ceiling" '
  { spent += $1 }
  $2 > 2 { cost[++full] = $1 }
  END {
    if (!full) exit 3
    median = full % 2 ? cost[(full + 1) / 2] : (cost[full / 2] + cost[full / 2 + 1]) / 2
    projection = spent + n * median
    if (projection > ceiling) {
      printf "spent %.2f, steps remaining %d, median %.2f, projection %.2f\n", spent, n, median, projection
      exit 1
    }
  }'

#!/usr/bin/env bash
# step-cost.sh — what one step of the run has spent on leaves so far, read off the run's
# `usage` events (issue #448).
#
# Usage:   step-cost.sh <step-text>     # run from the run's worktree
#
# harvest-usage.sh appends one `usage` event per finished leaf to .tdd/events.jsonl, carrying
# the leaf's `total_cost_usd` and the step it belongs to. This sums the events whose `step`
# equals <step-text> and prints the dollars to two decimals.
#
# **The figure is leaf spend only.** The conductor's own spending is in no `usage` event, so
# it is in no figure this script prints — never quote one as "what this step cost" in full.
set -uo pipefail

step="$1"

awk -v step="$step" '
  # value <line> <key> — the string value of "key": "…" on one event line, or empty.
  function value(line, key,    rest) {
    if (!match(line, "\"" key "\": \"[^\"]*\"")) return ""
    rest = substr(line, RSTART, RLENGTH)
    sub("^\"" key "\": \"", "", rest)
    sub("\"$", "", rest)
    return rest
  }
  value($0, "step") == step { sum += value($0, "total_cost_usd") }
  END { printf "%.2f\n", sum }
' .tdd/events.jsonl

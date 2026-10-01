#!/usr/bin/env bash
# step-cost.sh — what one step of the run has spent on leaves so far, read off the run's
# `usage` events.
#
# Usage:   step-cost.sh <step-text>     # run from the run's worktree
#          step-cost.sh --run           # the whole run, whatever step each event carries
#          step-cost.sh --steps         # one `<dollars> <leaves>` line per step
#
# harvest-usage.sh appends one `usage` event per finished leaf to .tdd/events.jsonl, carrying
# the leaf's `total_cost_usd` and the step it belongs to. This sums the events whose `step`
# equals <step-text> and prints the dollars to two decimals. A step no event carries yet —
# the state it is in before its first leaf has exited — prints nothing and exits 3: nothing
# to do, not an error. `--run` sums every event instead, including those carrying no step.
# `--steps` prints one `<dollars> <leaves>` line per step an event carries, in the order the
# log first mentions each; the leaf count tells a full step from a pin or a satisfied one.
#
# **The figure is leaf spend only.** The conductor's own spending is in no `usage` event, so
# it is in no figure this script prints — never quote one as "what this step cost" in full.
set -uo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"
USAGE='usage: step-cost.sh <step-text> | --run | --steps'
(( $# == 1 )) || refuse "step-cost.sh: expected exactly one argument, got $#"
step="$1" all=0 per_step=0
case "$step" in
  --run)   all=1 ;;
  --steps) per_step=1 ;;
  -*)
    refuse "step-cost.sh: unknown option '$step'" ;;
esac
if [[ ! -r .tdd/events.jsonl ]]; then
  echo "step-cost.sh: cannot read .tdd/events.jsonl in $PWD — run from the run's worktree" >&2
  exit 2
fi

source "$(dirname "${BASH_SOURCE[0]}")/lib/json-escape.sh"
json_escape_string escaped_step "$step"

# hazard: `awk -v` expands backslash escapes, so the escaped step goes through ENVIRON.
STEP_COST_STEP="$escaped_step" awk -v all="$all" -v per_step="$per_step" '
  function value(line, key,    rest) {
    if (!match(line, "\"" key "\": \"[^\"]*\"")) return ""
    rest = substr(line, RSTART, RLENGTH)
    sub("^\"" key "\": \"", "", rest)
    sub("\"$", "", rest)
    return rest
  }
  value($0, "event") != "usage" { next }
  per_step {
    s = value($0, "step")
    if (!(s in leaves)) order[++steps] = s
    dollars[s] += value($0, "total_cost_usd"); leaves[s]++; seen = 1
    next
  }
  all || value($0, "step") == ENVIRON["STEP_COST_STEP"] { sum += value($0, "total_cost_usd"); seen = 1 }
  END {
    if (!seen) exit 3
    if (per_step) {
      for (i = 1; i <= steps; i++) printf "%.2f %d\n", dollars[order[i]], leaves[order[i]]
      exit 0
    }
    printf "%.2f\n", sum
  }
' .tdd/events.jsonl

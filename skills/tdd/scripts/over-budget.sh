#!/usr/bin/env bash
# over-budget.sh — turn one recorded test-command run into a yes or no (issue #342, part
# of PRD #335). timed-test-run.sh records a tier and its seconds, tier-usual.sh says what
# that tier usually costs and time-budget.sh resolves the tunables; this is the one that
# compares them, so the conductor's narration has something to say a word about.
#
# Usage:   over-budget.sh <tier> <seconds> <usual>
#
# Exit 0 when the run is over budget, exit 1 when it is not — the clean negative CLAUDE.md's
# "Exit codes are the API" table reserves for a real answer: the check ran and said no.
# Nothing on stdout: the answer is the code, and the narration is the conductor's to write.
#
# Two rules, and either one answering yes is enough. The ratio rule is every tier's: a run
# whose seconds exceed VERI_TIME_WARN_RATIO times that tier's usual is over budget. The unit
# tier has a second, fixed ceiling on top of it — VERI_UNIT_BUDGET seconds — because it is
# the fast tier, and a fast tier that stopped being fast is over budget whatever its history
# says. So a unit run can be over budget by either rule, and a slow tier whose history is
# already slow is answered by the ratio alone.
#
# Both figures are read through time-budget.sh rather than re-read from the environment
# here, so the defaults and the refusal of a non-numeric value live in one place; a
# misconfigured run therefore leaves this script with exit 2, not a verdict.
#
# The comparison is awk's, not bash's: a recorded `seconds` is a decimal, and bash's `-gt`
# only compares integers — and the ratio rule is a multiplication besides. awk's own exit
# status is already this script's answer — `exit !(…)` is 0 when the run is over budget and
# 1 when it is not — so the comparison is `exec`'d rather than run and re-encoded, which
# also spares the run one process.
set -euo pipefail

tier="${1:?usage: over-budget.sh <tier> <seconds> <usual>}"
seconds="${2:?usage: over-budget.sh <tier> <seconds> <usual>}"
usual="${3:?usage: over-budget.sh <tier> <seconds> <usual>}"

HERE="$(cd "$(dirname "$0")" && pwd)"

# Two lines, seconds then ratio, split in bash rather than with head and tail so that the
# pair costs the one process time-budget.sh itself is, and so its exit 2 still stops us.
limits="$("$HERE/time-budget.sh")"
budget="${limits%%$'\n'*}"
ratio="${limits##*$'\n'}"

unit=0
if [[ "$tier" == "unit" ]]; then
  unit=1
fi

exec awk -v s="$seconds" -v b="$budget" -v r="$ratio" -v u="$usual" -v unit="$unit" \
  'BEGIN { exit !((unit && s > b) || s > r * u) }'

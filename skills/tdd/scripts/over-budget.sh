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
# The unit tier is the fast one, so it has a ceiling of its own — VERI_UNIT_BUDGET seconds —
# whatever its history says. That budget is read through time-budget.sh rather than re-read
# from the environment here, so the default and the refusal of a non-numeric value live in
# one place; a misconfigured run therefore leaves this script with exit 2, not a verdict.
#
# The comparison is awk's, not bash's: a recorded `seconds` is a decimal, and bash's `-gt`
# only compares integers. awk's own exit status is already this script's answer — `exit !(s >
# b)` is 0 when the run is over budget and 1 when it is not — so the comparison is `exec`'d
# rather than run and re-encoded, which also spares the run one process.
set -euo pipefail

tier="${1:?usage: over-budget.sh <tier> <seconds> <usual>}"
seconds="${2:?usage: over-budget.sh <tier> <seconds> <usual>}"
usual="${3:?usage: over-budget.sh <tier> <seconds> <usual>}"

HERE="$(cd "$(dirname "$0")" && pwd)"

budget="$("$HERE/time-budget.sh" | head -1)"

if [[ "$tier" == "unit" ]]; then
  exec awk -v s="$seconds" -v b="$budget" 'BEGIN { exit !(s > b) }'
fi

exit 1

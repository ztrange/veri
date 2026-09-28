#!/usr/bin/env bash
# over-budget.sh — turn one recorded test-command run into a yes or no.
# timed-test-run.sh records a tier and its seconds, tier-usual.sh says what
# that tier usually costs and time-budget.sh resolves the tunables; this is the one that
# compares them, so the conductor's narration has something to say a word about.
#
# Usage:   over-budget.sh <tier> <seconds> <usual>
#
# Exit 0 when the run is over budget, exit 1 when it is not — the clean negative CLAUDE.md's
# "Exit codes are the API" table reserves for a real answer: the check ran and said no.
#
# An over-budget run also prints exactly one line on stdout, carrying the ⏱ the conductor
# pastes into that phase's narration; a run that is not over budget prints nothing at all,
# so a conductor that pastes whatever it got narrates a warning only when there is one. The
# line is the whole of the answer's prose: the check never gates, and nothing branches on it.
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
# also spares the run one process. The tier goes to awk as itself rather than as a flag
# bash worked out first, so which tier the fixed ceiling belongs to is stated once, in the
# expression that applies it.
set -euo pipefail

# hazard: `${N:?}` aborts with status 1, this script's clean negative, so the arguments are checked by hand.
[[ $# -ge 3 && -n "$1" && -n "$2" && -n "$3" ]] || { echo "usage: over-budget.sh <tier> <seconds> <usual>" >&2; exit 2; }
tier="$1"
seconds="$2"
usual="$3"

HERE="$(cd "$(dirname "$0")" && pwd)"

limits="$("$HERE/time-budget.sh")"
budget="${limits%%$'\n'*}"
ratio="${limits##*$'\n'}"

exec awk -v s="$seconds" -v b="$budget" -v r="$ratio" -v u="$usual" -v tier="$tier" \
  'BEGIN {
     over = (tier == "unit" && s > b) || s > r * u
     if (over) printf "\342\217\261 %s tier took %s s (usual %s s, ratio %s, unit budget %s s)\n", tier, s, u, r, b
     exit !over
   }'

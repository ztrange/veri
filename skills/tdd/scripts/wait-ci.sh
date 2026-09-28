#!/usr/bin/env bash
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again.
#
# Usage:
#   wait-ci.sh <pr-url> [max-seconds]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, gh failed, unreadable rollup), or a
# check still pending past the deadline an earlier call recorded for the same head commit ·
# 3 a check is still pending, or none has appeared yet, when <max-seconds> run out.
#
# The deadline is recorded on the first call for a head commit, in .tdd/ci-deadline-<sha>.
#
# Tunables (env): VERI_POLL poll interval secs (default 10).
set -uo pipefail

[[ -n "${1:-}" ]] || { echo "usage: wait-ci.sh <pr-url> [max-seconds]" >&2; exit 2; }
pr="$1"
max="${2:-540}"
poll="${VERI_POLL:-10}"

deadline=""
inherited=""

rollup_state() {
  local doc
  doc="$(gh pr view "$pr" --json headRefOid,statusCheckRollup)" || return 2
  python3 -c '
import json, sys
doc = json.loads(sys.argv[1])
rows = doc.get("statusCheckRollup") or []
if not rows or any(r.get("status") != "COMPLETED" for r in rows):
    state = "pending"
elif all(r.get("conclusion") in ("SUCCESS", "NEUTRAL", "SKIPPED") for r in rows):
    state = "green"
else:
    state = "red"
print(state, doc.get("headRefOid") or "")
' "$doc"
}

while :; do
  read -r state head < <(rollup_state) && [[ -n "$head" ]] \
    || { echo "wait-ci.sh: could not read the checks of $pr" >&2; exit 2; }
  case "$state" in
    green) exit 0 ;;
    red) exit 1 ;;
  esac
  if [[ -z "$deadline" ]]; then
    mark=".tdd/ci-deadline-$head"
    if [[ -f "$mark" ]]; then
      deadline="$(< "$mark")"; inherited=1
    else
      deadline=$(( $(date +%s) + max )); echo "$deadline" > "$mark"
    fi
  fi
  if (( $(date +%s) >= deadline )); then
    [[ -n "$inherited" ]] && { echo "wait-ci.sh: checks of $pr still pending past the deadline recorded for $head" >&2; exit 2; }
    break
  fi
  sleep "$poll"
done

exit 3

#!/usr/bin/env bash
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again.
#
# Usage:
#   wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED, not all SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, gh failed, unreadable rollup), or a
# check still pending past the deadline an earlier call recorded for the same head commit ·
# 3 a check is still pending, none has appeared yet, every one was SKIPPED, or the PR still
# reports a head other than <head-sha>, when this call's <slice-seconds> run out.
#
# The deadline, <total-seconds> (default <slice-seconds>) after the first call for a head
# commit, is recorded in .tdd/ci-deadline-<sha>.
#
# Tunables (env): VERI_POLL poll interval secs (default 10).
set -uo pipefail

[[ -n "${1:-}" ]] || { echo "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]" >&2; exit 2; }
pr="$1"
max="${2:-540}"
total="${3:-$max}"
want="${4:-}"
poll="${VERI_POLL:-10}"

deadline=""
inherited=""
slice_end=""

rollup_state() {
  local doc
  doc="$(gh pr view "$pr" --json headRefOid,statusCheckRollup)" || return 2
  python3 -c '
import json, sys
doc = json.loads(sys.argv[1])
rows = doc.get("statusCheckRollup") or []
def outcome(r):
    if r.get("__typename") == "StatusContext":
        if "state" not in r:
            sys.exit(2)
        return None if r.get("state") in ("PENDING", "EXPECTED") else r.get("state")
    return r.get("conclusion") if r.get("status") == "COMPLETED" else None
outcomes = [outcome(r) for r in rows]
if not rows or None in outcomes or all(o == "SKIPPED" for o in outcomes):
    state = "pending"
elif all(o in ("SUCCESS", "NEUTRAL", "SKIPPED") for o in outcomes):
    state = "green"
else:
    state = "red"
print(state, doc.get("headRefOid") or "")
' "$doc"
}

sha_state() {
  local repo
  repo="${pr#https://github.com/}"; repo="${repo%/pull/*}"
  gh api "repos/$repo/commits/$1/check-runs" > /dev/null || return 2
  echo pending
}

while :; do
  read -r state head < <(rollup_state) && [[ -n "$head" ]] \
    || { echo "wait-ci.sh: could not read the checks of $pr" >&2; exit 2; }
  [[ -n "$want" && "$head" != "$want" ]] && state=pending
  if [[ -n "$want" && "$state" == green ]]; then
    state="$(sha_state "$want")" || { echo "wait-ci.sh: could not read the checks of $want" >&2; exit 2; }
  fi
  case "$state" in
    green) exit 0 ;;
    red) exit 1 ;;
  esac
  now="$(date +%s)"
  if [[ -z "$deadline" ]]; then
    slice_end=$(( now + max ))
    key="${want:-$head}"
    mark=".tdd/ci-deadline-$key"
    if [[ -f "$mark" ]]; then
      deadline="$(< "$mark")"; inherited=1
    else
      deadline=$(( now + total )); echo "$deadline" > "$mark"
    fi
  fi
  if (( now >= deadline )); then
    [[ -n "$inherited" ]] && { echo "wait-ci.sh: checks of $pr still pending past the deadline recorded for $key" >&2; exit 2; }
    break
  fi
  (( now >= slice_end )) && break
  sleep "$poll"
done

exit 3

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
repo="${pr#https://github.com/}"; repo="${repo%/pull/*}"
max="${2:-540}"
total="${3:-$max}"
want="${4:-}"
poll="${VERI_POLL:-10}"

deadline=""
inherited=""
slice_end=""
passing="success neutral skipped"

pr_head() {
  local doc
  doc="$(gh pr view "$pr" --json headRefOid,statusCheckRollup)" || return 2
  python3 -c '
import json, sys
doc = json.loads(sys.argv[1])
if any(r.get("__typename") == "StatusContext" and "state" not in r
       for r in doc.get("statusCheckRollup") or []):
    sys.exit(2)
print(doc.get("headRefOid") or "")
' "$doc"
}

sha_state() {
  local runs
  runs="$(gh api --paginate --slurp "repos/$repo/commits/$1/check-runs")" || return 2
  local statuses
  statuses="$(gh api "repos/$repo/commits/$1/status")" || return 2
  python3 -c '
import json, sys
pages = json.loads(sys.argv[1])
states = [s.get("state") for s in json.loads(sys.argv[2]).get("statuses") or []]
runs = [r for p in pages for r in p.get("check_runs") or []]
outcomes = [r.get("conclusion") if r.get("status") == "completed" else None for r in runs]
if any(o is not None and o not in sys.argv[3].split() for o in outcomes) \
        or any(s in ("failure", "error") for s in states):
    print("red")
elif None in outcomes or all(o == "skipped" for o in outcomes) \
        or "pending" in states:
    print("pending")
else:
    print("green")
' "$runs" "$statuses" "$passing"
}

while :; do
  read -r head < <(pr_head) && [[ -n "$head" ]] \
    || { echo "wait-ci.sh: could not read the checks of $pr" >&2; exit 2; }
  if [[ -n "$want" && "$head" != "$want" ]]; then
    state=pending
  else
    state="$(sha_state "$head")" || { echo "wait-ci.sh: could not read the checks of $head" >&2; exit 2; }
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

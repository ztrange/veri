#!/usr/bin/env bash
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again.
#
# Usage:
#   wait-ci.sh <pr-url> [max-seconds]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, gh failed, unreadable rollup) ·
# 3 a check is still pending, or none has appeared yet, when <max-seconds> run out.
#
# Tunables (env): VERI_POLL poll interval secs (default 10).
set -uo pipefail

[[ -n "${1:-}" ]] || { echo "usage: wait-ci.sh <pr-url> [max-seconds]" >&2; exit 2; }
pr="$1"
max="${2:-540}"
poll="${VERI_POLL:-10}"

deadline=$(( $(date +%s) + max ))

rollup_state() {
  local doc
  doc="$(gh pr view "$pr" --json statusCheckRollup)" || return 2
  python3 -c '
import json, sys
rows = json.loads(sys.argv[1]).get("statusCheckRollup") or []
if not rows or any(r.get("status") != "COMPLETED" for r in rows):
    print("pending")
elif all(r.get("conclusion") in ("SUCCESS", "NEUTRAL", "SKIPPED") for r in rows):
    print("green")
else:
    print("red")
' "$doc"
}

while :; do
  state="$(rollup_state)" || { echo "wait-ci.sh: could not read the checks of $pr" >&2; exit 2; }
  case "$state" in
    green) exit 0 ;;
    red) exit 1 ;;
  esac
  (( $(date +%s) >= deadline )) && break
  sleep "$poll"
done

exit 3

#!/usr/bin/env bash
# parallel-conductors.sh — rung 3 of the scope ladder: run several issue-conductors at once
# over the solvable set, from the target repo's primary checkout (#102).
#
# VERI_PARALLEL is how many conductors run at once, default 1. N conductors are N concurrent
# `claude -p` sessions, billed as such, so a value that is not a whole number >= 1 — zero, a
# word, set-but-empty — is a misconfigured run, not a decision: a diagnostic on stderr and
# exit 2 before anything is launched, never a guess at how much to spend.
#
# Usage:   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
set -euo pipefail

parallel="${VERI_PARALLEL-1}"

if [[ ! "$parallel" =~ ^[0-9]+$ ]] || (( 10#$parallel < 1 )); then
  echo "parallel-conductors: VERI_PARALLEL must be a whole number >= 1: '$parallel'" >&2
  exit 2
fi

HERE="$(cd "$(dirname "$0")" && pwd)"

# VERI_MAX_ISSUES caps the launches of one invocation, as at rung 2; 0, the default, is no cap.
max_issues="${VERI_MAX_ISSUES:-0}"

# The loop: while fewer than VERI_PARALLEL conductors are in flight — launched here and not yet
# seen to finish — select with solvable-issues.sh and launch the first printed issue this
# invocation has not launched yet, in the background: one it already ran and saw finish may still
# be printed (a run that left no claim behind), and is never launched a second time. Then wait
# for whichever in-flight conductor ends first and select again: a blocker only closes when a
# human merges, so the set is recomputed after every completion rather than cached. With nothing
# in flight and nothing left to launch, the loop ends with solvable-issues.sh's own status —
# exit 3 once nothing is left.
declare -A in_flight=()   # issue number -> pid of its supervise.sh
declare -A launched=()    # every issue number this invocation has launched
order=()                  # the same numbers, in launch order: the order the report follows

# report — one line per launched issue, in launch order, its outcome read from its PR and its
# run's event log rather than the conductor's exit code, which is 0 for a finished run and a
# bail alike: a ready PR saying `Closes #<n>` is done; a draft one whose `.tdd/wt/<n>` event log
# ends in a bail is bailed.
report() {
  local prs n pr last
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    prs="$(cat "$VERI_GH_JSON/prs.json")"
  else
    prs="$(gh pr list --state open --limit 10000 --json body,isDraft,url)"
  fi
  for n in "${order[@]+"${order[@]}"}"; do
    pr="$(python3 -c '
import json, re, sys
for pr in json.loads(sys.argv[1]):
    if sys.argv[2] in re.findall(r"\bCloses #(\d+)", pr.get("body") or ""):
        print("draft" if pr.get("isDraft") else "ready", pr.get("url", ""))
        break
' "$prs" "$n")"
    last="$(tail -n 1 ".tdd/wt/$n/.tdd/events.jsonl" 2>/dev/null || true)"
    case "$pr" in
      ready\ *) echo "#$n — done ${pr#ready }" ;;
      draft\ *) [[ "$last" == *'"event": "bail"'* ]] && echo "#$n — bailed ${pr#draft }" ;;
    esac
  done
  return 0
}
while :; do
  while (( ${#in_flight[@]} < 10#$parallel )); do
    (( max_issues == 0 || ${#launched[@]} < max_issues )) || break
    solvable="$("$HERE/solvable-issues.sh")" && rc=0 || rc=$?
    (( rc == 0 )) || break
    n=""
    for candidate in $solvable; do
      [[ -n "${launched[$candidate]:-}" ]] || { n="$candidate"; break; }
    done
    [[ -n "$n" ]] || break
    "$HERE/supervise.sh" "conductor-$n" "$HERE/run-conductor.sh" "$n" > /dev/null &
    in_flight[$n]=$!
    launched[$n]=1
    order+=("$n")
  done
  if (( ${#in_flight[@]} == 0 )); then
    report
    exit "${rc:-3}"
  fi
  wait -n || true
  for n in "${!in_flight[@]}"; do
    kill -0 "${in_flight[$n]}" 2>/dev/null || unset "in_flight[$n]"
  done
done

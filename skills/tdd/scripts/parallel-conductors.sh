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

# --continue-on-bail keeps launching past a bailed or killed conductor; without it the first one
# stops new launches, and the conductors already running are still waited to completion.
continue_on_bail=""
[[ "${1:-}" == --continue-on-bail ]] && continue_on_bail=1

# VERI_MAX_ISSUES caps the launches of one invocation, as at rung 2; 0, the default, is no cap.
max_issues="${VERI_MAX_ISSUES:-0}"

# VERI_RUN_TIMEOUT is the wall-clock cap on one conductor, and the figure a killed one is reported
# with — a killed conductor is not retried here; /tdd <n> resumes it.
run_timeout="${VERI_RUN_TIMEOUT:-14400}"

# The outer supervise.sh runs with heartbeat and timeout both VERI_RUN_TIMEOUT and no stuck
# retries — pinned equal, because a conductor's stdout is silent for the length of a leaf. Those
# values are for the outer supervisor only: the conductor gets the caller's own four leaf
# tunables back exactly as they were, set or unset, through `env` — leaking
# VERI_STUCK_RETRIES=0 into a conductor once turned its own baseline red (#87).
# `env -u` strips all four, then the caller's set ones are re-added as they were.
caller_env=()
caller_set=()
for var in VERI_HEARTBEAT VERI_TIMEOUT VERI_STUCK_RETRIES VERI_POLL; do
  caller_env+=(-u "$var")
  [[ -n "${!var+set}" ]] && caller_set+=("$var=${!var}")
done
caller_env+=("${caller_set[@]+"${caller_set[@]}"}")

# The launcher's supervisors write `.tdd/conductor-<n>.{log,rc,exit}` into the caller's checkout,
# and each conductor's first check is that `git status --porcelain` there is empty. So `.tdd/*` goes
# into the shared info/exclude before anything is written — never the .gitignore, which is tracked
# and would dirty the very tree it is meant to keep clean. --git-common-dir resolves a linked
# worktree back to the primary's git dir, which every worktree reads, and answers relative to the
# current directory when it answers relatively. Only when the line is absent, so a second
# invocation does not grow the file.
common_dir="$(git rev-parse --git-common-dir)"
exclude="$common_dir/info/exclude"
if ! grep -xF '.tdd/*' "$exclude" > /dev/null 2>&1; then
  mkdir -p "$common_dir/info"
  if [[ -s "$exclude" && -n "$(tail -c 1 "$exclude")" ]]; then
    echo "" >> "$exclude"
  fi
  echo '.tdd/*' >> "$exclude"
fi

# A conductor whose supervise.sh exits non-zero leaves that status in this directory, one file
# per issue: exit 2 there is a conductor its supervisor killed.
rc_dir="$(mktemp -d)"
trap 'rm -rf "$rc_dir"' EXIT

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

# prs_json — the open PRs: the VERI_GH_JSON fixture when one is set.
prs_json() {
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/prs.json"
  else
    gh pr list --state open --limit 10000 --json body,isDraft,url
  fi
}

# outcome <n> <prs> — issue <n>'s outcome, read from its PR and its run's event log rather than
# the conductor's exit code, which is 0 for a finished run and a bail alike: `killed after
# <VERI_RUN_TIMEOUT>s` when its supervise.sh exited 2, `done <url>` for a ready PR saying `Closes #<n>`, `bailed <url>` for a
# draft one whose `.tdd/wt/<n>` event log ends in a bail; nothing otherwise.
outcome() {
  local n="$1" prs="$2" pr last
  if [[ "$(cat "$rc_dir/$n" 2>/dev/null)" == 2 ]]; then
    echo "killed after ${run_timeout}s"
    return 0
  fi
  pr="$(python3 -c '
import json, re, sys
for pr in json.loads(sys.argv[1]):
    if sys.argv[2] in re.findall(r"\bCloses #(\d+)", pr.get("body") or ""):
        print("draft" if pr.get("isDraft") else "ready", pr.get("url", ""))
        break
' "$prs" "$n")"
  case "$pr" in
    ready\ *) echo "done ${pr#ready }" ;;
    draft\ *)
      last="$(tail -n 1 ".tdd/wt/$n/.tdd/events.jsonl" 2>/dev/null || true)"
      [[ "$last" == *'"event": "bail"'* ]] && echo "bailed ${pr#draft }" ;;
  esac
  return 0
}

# report — one line per launched issue, in launch order.
report() {
  local prs n got
  prs="$(prs_json)"
  for n in "${order[@]+"${order[@]}"}"; do
    got="$(outcome "$n" "$prs")"
    [[ -z "$got" ]] || echo "#$n — $got"
  done
  return 0
}
stopped=""   # set once a bail or kill has stopped new launches
while :; do
  while (( ${#in_flight[@]} < 10#$parallel )); do
    [[ -z "$stopped" ]] || break
    (( max_issues == 0 || ${#launched[@]} < max_issues )) || break
    solvable="$("$HERE/solvable-issues.sh")" && rc=0 || rc=$?
    (( rc == 0 )) || break
    n=""
    for candidate in $solvable; do
      [[ -n "${launched[$candidate]:-}" ]] || { n="$candidate"; break; }
    done
    [[ -n "$n" ]] || break
    (
      VERI_HEARTBEAT="$run_timeout" VERI_TIMEOUT="$run_timeout" VERI_STUCK_RETRIES=0 \
        "$HERE/supervise.sh" "conductor-$n" env "${caller_env[@]}" "$HERE/run-conductor.sh" "$n" > /dev/null \
        || echo "$?" > "$rc_dir/$n"
    ) &
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
    kill -0 "${in_flight[$n]}" 2>/dev/null && continue
    unset "in_flight[$n]"
    if [[ -z "$continue_on_bail" ]]; then
      case "$(outcome "$n" "$(prs_json)")" in
        killed\ *|bailed\ *) stopped=1 ;;
      esac
    fi
  done
done

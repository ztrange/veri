#!/usr/bin/env bash
# parallel-conductors.sh — rung 3 of the scope ladder: run several issue-conductors at once
# over the solvable set, from the target repo's primary checkout.
#
# VERI_PARALLEL is how many conductors run at once, default 1. N conductors are N concurrent
# `claude -p` sessions, billed as such, so a value that is not a whole number >= 1 — zero, a
# word, set-but-empty — is a misconfigured run, not a decision: a diagnostic on stderr and
# exit 2 before anything is launched, never a guess at how much to spend.
#
# Usage:   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/appendable.sh"
source "$HERE/lib/github.sh"

continue_on_bail=""
[[ "${1:-}" == --continue-on-bail ]] && continue_on_bail=1

max_issues="${VERI_MAX_ISSUES-0}"

run_timeout="${VERI_RUN_TIMEOUT:-14400}"

caller_env=()
caller_set=()
for var in VERI_HEARTBEAT VERI_TIMEOUT VERI_STUCK_RETRIES VERI_POLL; do
  caller_env+=(-u "$var")
  [[ -n "${!var+set}" ]] && caller_set+=("$var=${!var}")
done
caller_env+=("${caller_set[@]+"${caller_set[@]}"}")

common_dir="$(git rev-parse --git-common-dir)"
exclude="$common_dir/info/exclude"
if ! grep -xF '.tdd/*' "$exclude" > /dev/null 2>&1; then
  make_appendable "$exclude"
  echo '.tdd/*' >> "$exclude"
fi

finish() {
  mkdir -p .tdd
  echo "$1" > .tdd/parallel.exit
  exit "$(to_contract "$1")"
}

require_whole_number() {
  local floor="${3:-1}"
  if [[ ! "$2" =~ ^[0-9]+$ ]] || (( 10#$2 < floor )); then
    echo "parallel-conductors: $1 must be a whole number >= $floor: '$2'" >&2
    finish 2
  fi
}

budget="${VERI_CONDUCTOR_CTX_BUDGET:-120000}"
require_whole_number VERI_CONDUCTOR_CTX_BUDGET "$budget" 0
poll="${VERI_POLL:-1}"

parallel="${VERI_PARALLEL-1}"
require_whole_number VERI_PARALLEL "$parallel"
[[ -n "${VERI_MAX_ISSUES+set}" ]] && require_whole_number VERI_MAX_ISSUES "$max_issues"

rc_dir="$(mktemp -d)"
at_exit 'rm -rf "$rc_dir" || exit 2'

declare -A in_flight=()   # issue number -> pid of its supervise.sh
declare -A launched=()    # every issue number this invocation has launched
order=()                  # the same numbers, in launch order: the order the report follows

prs_json() {
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/prs.json"
  else
    gh_list "repos/{owner}/{repo}/pulls?state=open&per_page=100" pr list --state open --limit 10000 --json body,isDraft,url
  fi
}

outcome() {
  local n="$1" prs="$2" pr last
  if [[ "$(cat "$rc_dir/$n" 2>/dev/null)" == 2 ]]; then
    echo "killed after ${run_timeout}s"
    return 0
  fi
  [[ ! -e ".tdd/parked/$n.md" ]] || return 0
  pr="$(PYTHONPATH="$HERE/lib" python3 -c '
import re, sys
from json_documents import items
for pr in items(sys.stdin.read()):
    if sys.argv[1] in re.findall(r"\bCloses #(\d+)", pr.get("body") or ""):
        print("draft" if pr.get("isDraft", pr.get("draft")) else "ready", pr.get("html_url", pr.get("url", "")))
        break
' "$n" <<< "$prs")"
  case "$pr" in
    ready\ *) echo "done ${pr#ready }" ;;
    draft\ *)
      last="$(tail -n 1 ".tdd/wt/$n/.tdd/events.jsonl" 2>/dev/null || true)"
      [[ "$last" == *'"event": "bail"'* ]] && echo "bailed ${pr#draft }" ;;
  esac
  return 0
}

follow_log() {
  local line part=""
  until [[ -e "$2" ]]; do
    kill -0 "$1" 2>/dev/null || return 0
    sleep "$poll"
  done
  exec 3< "$2"
  while :; do
    local alive=0
    kill -0 "$1" 2>/dev/null && alive=1
    while IFS= read -r line <&3; do
      printf '%s\n' "$part$line"
      part=""
    done
    part+="$line"
    (( alive )) || break
    sleep "$poll"
  done
}

print_context() {
  local line read_re='"cache_read_input_tokens":([0-9]+)' create_re='"cache_creation_input_tokens":([0-9]+)'
  local cache_read context=0 step_done=0
  while IFS= read -r line; do
    if (( step_done )) && [[ $line == *'"type":"user"'* ]]; then
      if (( context > budget )); then
        : > "$rc_dir/$1.restart"
        kill -TERM "$2" 2>/dev/null || true
        return 0
      fi
      step_done=0
    fi
    [[ $line == *'"type":"assistant"'* ]] || continue
    [[ $line == *'event.sh step-done'* ]] && step_done=1
    [[ $line =~ $read_re ]] || continue
    cache_read=${BASH_REMATCH[1]}
    [[ $line =~ $create_re ]] || continue
    context=$((cache_read + BASH_REMATCH[1]))
    echo "context $1 $context"
  done
}

is_failure() {
  case "$1" in killed\ *|bailed\ *) return 0 ;; esac
  return 1
}

failed=""
report() {
  local prs n got
  prs="$(prs_json)"
  for n in "${order[@]+"${order[@]}"}"; do
    got="$(outcome "$n" "$prs")"
    [[ -z "$got" ]] || echo "#$n — $got"
    if is_failure "$got"; then failed=1; fi
  done
  return 0
}
launch() {
  local n="$1"
  rm -f "$rc_dir/$n"
  (
    rm -f ".tdd/conductor-$n.log"
    VERI_HEARTBEAT="$run_timeout" VERI_TIMEOUT="$run_timeout" VERI_STUCK_RETRIES=0 \
      "$HERE/supervise.sh" "conductor-$n" env "${caller_env[@]}" "$HERE/run-conductor.sh" "$n" \
      > /dev/null &
    sup=$!
    follow_log "$sup" ".tdd/conductor-$n.log" | print_context "$n" "$sup"
    wait "$sup" || echo "$?" > "$rc_dir/$n"
  ) &
  in_flight[$n]=$!
}

declare -A restart=()     # issue numbers stopped over budget, to be launched again first
stopped=""   # set once a bail or kill has stopped new launches: `#<n> bailed` or `#<n> killed`
plumbing=""  # set once solvable-issues.sh has exited 2
why=""       # what last kept the loop from launching, for the report's closing line
while :; do
  while (( ${#in_flight[@]} < 10#$parallel )); do
    n=""
    for candidate in "${!restart[@]}"; do n="$candidate"; break; done
    if [[ -n "$n" ]]; then
      unset "restart[$n]"
      echo "restarted $n"
      launch "$n"
      continue
    fi
    [[ -z "$stopped" ]] || break
    (( max_issues == 0 || ${#launched[@]} < max_issues )) || { why="VERI_MAX_ISSUES reached"; break; }
    solvable="$("$HERE/solvable-issues.sh")" && rc=0 || rc=$?
    why="nothing solvable"
    (( rc != 2 )) || { plumbing=1; why="solvable-issues.sh could not answer"; }
    (( rc == 0 )) || break
    n=""
    for candidate in $solvable; do
      [[ -n "${launched[$candidate]:-}" ]] || { n="$candidate"; break; }
    done
    [[ -n "$n" ]] || break
    launch "$n"
    launched[$n]=1
    order+=("$n")
  done
  if (( ${#in_flight[@]} == 0 )); then
    report
    echo "stopped: ${stopped:-$why}"
    [[ -z "$plumbing" ]] || finish 2
    [[ -z "$failed" ]] || finish 1
    (( ${#order[@]} > 0 )) || finish 3
    finish 0
  fi
  wait -n || true
  for n in "${!in_flight[@]}"; do
    kill -0 "${in_flight[$n]}" 2>/dev/null && continue
    unset "in_flight[$n]"
    if [[ -e "$rc_dir/$n.restart" ]]; then
      rm -f "$rc_dir/$n.restart"
      restart[$n]=1
      continue
    fi
    if [[ -e ".tdd/parked/$n.md" ]]; then
      echo "parked $n"
      continue
    fi
    got="$(outcome "$n" "$(prs_json)")"
    if [[ -z "$continue_on_bail" && -z "$stopped" ]] && is_failure "$got"; then
      stopped="#$n ${got%% *}"
    fi
  done
done

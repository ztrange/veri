#!/usr/bin/env bash
# ledger-steps.sh — print lib/ledger.sh's `ledger_steps` records for the ledger on stdin.
#
# Usage:   ledger-steps.sh [current|last-done] < .tdd/issue-<n>.md
#          ledger-steps.sh criterion <k> < issue-body.md
#
#   (none)    every record
#   current   the first refactor-pending step's text, else the first open step's; exit 3 if neither
#   last-done the last done step's text; exit 3 if none
#   criterion the k-th checkbox's text under `## Acceptance criteria`; exit 3 if fewer than k
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/ledger.sh"

USAGE="usage: ledger-steps.sh [current|last-done|criterion <k>]"

texts() {
  local record index state kind pending added criterion text
  while IFS= read -r record; do
    ledger_fields "$record"
    "$1" && printf '%s\n' "$text"
  done
  return 0
}

is_pending() { [[ "$state" == done && "$pending" == 1 ]]; }
is_open_step() { [[ "$state" == open && ( "$kind" == step || "$kind" == diff-checked ) ]]; }
is_done() { [[ "$state" == done ]]; }
is_any() { :; }

current() {
  local records select found
  records="$(ledger_steps)"
  for select in is_pending is_open_step; do
    mapfile -t found < <(texts "$select" <<< "$records")
    ((${#found[@]})) || continue
    printf '%s\n' "${found[0]}"
    return 0
  done
  return 3
}

last_done() {
  local found
  mapfile -t found < <(ledger_steps | texts is_done)
  ((${#found[@]})) || return 3
  printf '%s\n' "${found[-1]}"
}

criterion() {
  local k=$((10#$1)) line in_section=0 found
  mapfile -t found < <(
    while IFS= read -r line || [[ -n "$line" ]]; do
      if [[ "$line" == '## '* ]]; then
        in_section=0
        [[ "$line" == '## Acceptance criteria'* ]] && in_section=1
      fi
      ((in_section)) && printf '%s\n' "$line"
    done | ledger_steps | texts is_any
  )
  ((k >= 1 && k <= ${#found[@]})) || return 3
  printf '%s\n' "${found[k - 1]}"
}

case "${1:-}" in
  current) current ;;
  last-done) last_done ;;
  criterion) [[ "${2:-}" =~ ^[0-9]+$ ]] || refuse; criterion "$2" ;;
  '') ledger_steps ;;
  *) refuse ;;
esac

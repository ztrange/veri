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

TEXT=$'\t[^\t]*\t[^\t]*\t(.*)$'

current() {
  local records record pattern
  records="$(ledger_steps)"
  for pattern in $'^[0-9]+\tdone\t[^\t]*\t1'"$TEXT" \
                 $'^[0-9]+\topen\tstep\t[^\t]*'"$TEXT"; do
    while IFS= read -r record; do
      [[ "$record" =~ $pattern ]] || continue
      printf '%s\n' "${BASH_REMATCH[1]}"
      return 0
    done <<< "$records"
  done
  return 3
}

last_done() {
  local record last='' found=0 pattern=$'^[0-9]+\tdone\t[^\t]*\t[^\t]*'"$TEXT"
  while IFS= read -r record; do
    [[ "$record" =~ $pattern ]] && last="${BASH_REMATCH[1]}" found=1
  done <<< "$(ledger_steps)"
  ((found)) || return 3
  printf '%s\n' "$last"
}

criterion() {
  local k="$1" line in_section=0 record pattern=$'^[0-9]+\t[^\t]*\t[^\t]*\t[^\t]*'"$TEXT"
  while IFS= read -r record; do
    k=$((k - 1))
    ((k == 0)) || continue
    [[ "$record" =~ $pattern ]] && printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  done < <(
    while IFS= read -r line || [[ -n "$line" ]]; do
      if [[ "$line" == '## '* ]]; then
        in_section=0
        [[ "$line" == '## Acceptance criteria'* ]] && in_section=1
      fi
      ((in_section)) && printf '%s\n' "$line"
    done | ledger_steps
  )
  return 3
}

case "${1:-}" in
  current) current ;;
  last-done) last_done ;;
  criterion) criterion "$2" ;;
  *) ledger_steps ;;
esac

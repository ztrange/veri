#!/usr/bin/env bash
# ledger-steps.sh — print lib/ledger.sh's `ledger_steps` records for the ledger on stdin.
#
# Usage:   ledger-steps.sh [current] < .tdd/issue-<n>.md
#
#   (none)    every record
#   current   the first refactor-pending step's text, else the first open step's; exit 3 if neither
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/ledger.sh"

current() {
  local records record pattern
  records="$(ledger_steps)"
  for pattern in $'^[0-9]+\tdone\t[^\t]*\t1\t[^\t]*\t[^\t]*\t(.*)$' \
                 $'^[0-9]+\topen\tstep\t[^\t]*\t[^\t]*\t[^\t]*\t(.*)$'; do
    while IFS= read -r record; do
      [[ "$record" =~ $pattern ]] || continue
      printf '%s\n' "${BASH_REMATCH[1]}"
      return 0
    done <<< "$records"
  done
  return 3
}

case "${1:-}" in
  current) current ;;
  *) ledger_steps ;;
esac

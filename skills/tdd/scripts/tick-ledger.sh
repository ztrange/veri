#!/usr/bin/env bash
# tick-ledger.sh [--refactor-pending] <ledger-file> <matcher> — check off one step in the
# local ledger.
#
# Thin file wrapper around lib/ledger.sh's ledger_tick: flips the first unchecked `- [ ]`
# step containing <matcher> to `- [x]`, in place. The conductor stages and commits the
# ledger together with the step's green code, so git and ledger never diverge. Exit 3 if no
# unchecked step matched — the file is left untouched.
#
# --refactor-pending also appends lib/ledger.sh's pending mark to that same line in the same
# write, so the green commit records that the step is green but not yet tidied. Without the
# flag the line is ticked with no mark.
#
# Usage:   tick-ledger.sh [--refactor-pending] .tdd/issue-<n>.md '<substring of the step>'
set -euo pipefail

USAGE="usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>"

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"

pending=""
if [[ "${1:-}" == "--refactor-pending" ]]; then
  pending=pending
  shift
fi

require_args 1 "$@"
file="$1"
matcher="${2:-}"
source "$HERE/lib/ledger.sh"

new="$(ledger_tick "$matcher" $pending < "$file")" || exit "$(to_contract $?)"

printf '%s\n' "$new" > "$file"

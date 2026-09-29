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

pending=""
if [[ "${1:-}" == "--refactor-pending" ]]; then
  pending=pending
  shift
fi

[[ -n "${1:-}" ]] || { echo "usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>" >&2; exit 2; }
file="$1"
matcher="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/ledger.sh"

new="$(ledger_tick "$matcher" $pending < "$file")" || exit $?

printf '%s\n' "$new" > "$file"

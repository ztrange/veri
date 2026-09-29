#!/usr/bin/env bash
# clear-refactor-pending.sh <ledger-file> <matcher> — drop the pending mark from one step in
# the local ledger.
#
# Thin file wrapper around lib/ledger.sh's ledger_clear_pending, the counterpart of
# `tick-ledger.sh --refactor-pending`: strips the mark from the first ticked step that
# contains <matcher> and carries it, in place, and exits 0. Exit 3 if no such step matched —
# the file is left byte-identical, because nothing is written unless the transform found
# its line.
#
# Usage:   clear-refactor-pending.sh .tdd/issue-<n>.md '<substring of the step>'
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: clear-refactor-pending.sh <ledger-file> <matcher>" >&2; exit 2; }
file="$1"
matcher="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/ledger.sh"

new="$(ledger_clear_pending "$matcher" < "$file")" || exit $?

printf '%s\n' "$new" > "$file"

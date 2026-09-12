#!/usr/bin/env bash
# tick-ledger.sh <ledger-file> <matcher> — check off one step in the local ledger.
#
# Thin file wrapper around tick-criterion.sh (the tested pure transform): flips the first
# unchecked `- [ ]` step containing <matcher> to `- [x]`, in place. The conductor stages
# and commits the ledger together with the step's green code, so git and ledger never
# diverge. Exit 3 (from tick-criterion.sh) if no unchecked step matched — the file is left
# untouched.
#
# Usage:   tick-ledger.sh .tdd/issue-<n>.md '<distinctive substring of the step>'
set -euo pipefail

file="${1:?usage: tick-ledger.sh <ledger-file> <matcher>}"
matcher="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"

new="$("$HERE/tick-criterion.sh" "$matcher" < "$file")" || exit $?
printf '%s\n' "$new" > "$file"

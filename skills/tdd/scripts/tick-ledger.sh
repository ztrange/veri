#!/usr/bin/env bash
# tick-ledger.sh [--refactor-pending] <ledger-file> <matcher> — check off one step in the
# local ledger.
#
# Thin file wrapper around tick-criterion.sh (the tested pure transform): flips the first
# unchecked `- [ ]` step containing <matcher> to `- [x]`, in place. The conductor stages
# and commits the ledger together with the step's green code, so git and ledger never
# diverge. Exit 3 (from tick-criterion.sh) if no unchecked step matched — the file is left
# untouched.
#
# --refactor-pending appends ` ⟂ refactor pending` to that same line in the same write, so
# the green commit records that the step is green but not yet tidied. Without the flag the
# line is ticked with no mark.
#
# Usage:   tick-ledger.sh [--refactor-pending] .tdd/issue-<n>.md '<substring of the step>'
set -euo pipefail

mark=""
if [[ "${1:-}" == "--refactor-pending" ]]; then
  mark=" ⟂ refactor pending"
  shift
fi

file="${1:?usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>}"
matcher="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"

new="$("$HERE/tick-criterion.sh" "$matcher" < "$file")" || exit $?

# The marked line is the one tick-criterion.sh changed: read the pre-tick file and the
# transformed text as two inputs, and mark the first line where they differ. Line counts
# match, so FNR — awk's per-input line number — indexes both.
if [[ -n "$mark" ]]; then
  new="$(MARK="$mark" awk '
    NR == FNR { before[FNR] = $0; next }
    {
      if (!done && $0 != before[FNR]) { $0 = $0 ENVIRON["MARK"]; done = 1 }
      print
    }
  ' "$file" - <<< "$new")"
fi

printf '%s\n' "$new" > "$file"

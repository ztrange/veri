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

[[ -n "${1:-}" ]] || { echo "usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>" >&2; exit 2; }
file="$1"
matcher="${2:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"

# mark_ticked_line <pre-tick-file> <mark>  < ticked-text -> that text on stdout, with <mark>
# appended to the one line tick-criterion.sh changed. Which line that is, is read off the
# two texts rather than re-derived: the pre-tick file and the ticked text go in as awk's two
# inputs, and the first line where they differ is the tick. Line counts match, so FNR —
# awk's per-input line number — indexes both, and `-` is the ticked text on stdin.
mark_ticked_line() {
  local before="$1"
  MARK="$2" awk '
    BEGIN { mark = ENVIRON["MARK"]; done = 0 }
    NR == FNR { before[FNR] = $0; next }
    {
      if (!done && $0 != before[FNR]) { $0 = $0 mark; done = 1 }
      print
    }
  ' "$before" -
}

new="$("$HERE/tick-criterion.sh" "$matcher" < "$file")" || exit $?

if [[ -n "$mark" ]]; then
  new="$(mark_ticked_line "$file" "$mark" <<< "$new")"
fi

printf '%s\n' "$new" > "$file"

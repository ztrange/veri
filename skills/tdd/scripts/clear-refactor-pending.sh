#!/usr/bin/env bash
# clear-refactor-pending.sh <ledger-file> <matcher> — drop the ` ⟂ refactor pending` mark
# from one step in the local ledger.
#
# The counterpart of `tick-ledger.sh --refactor-pending`: that appends the mark with the
# step's green commit, this removes it once the step has been tidied and verified. Strips
# the mark from the FIRST `- [x]` step that both contains <matcher> and carries the mark,
# in place, and exits 0. Exit 3 if no such step matched — the file is left byte-identical,
# because nothing is written unless the transform found its line.
#
# Usage:   clear-refactor-pending.sh .tdd/issue-<n>.md '<substring of the step>'
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: clear-refactor-pending.sh <ledger-file> <matcher>" >&2; exit 2; }
file="$1"
matcher="${2:-}"

mark=' ⟂ refactor pending'

strip_mark() {
  MATCHER="$2" MARK="$3" awk '
    BEGIN {
      matcher = ENVIRON["MATCHER"]; mark = ENVIRON["MARK"]; done = 0
      ticked = "^[[:space:]]*-[[:space:]]\\[x\\]"
    }
    {
      if (!done && $0 ~ ticked && index($0, matcher) > 0 && sub(mark "$", "")) {
        done = 1
      }
      print
    }
    END { if (!done) exit 3 }
  ' "$1"
}

new="$(strip_mark "$file" "$matcher" "$mark")" || exit $?

printf '%s\n' "$new" > "$file"

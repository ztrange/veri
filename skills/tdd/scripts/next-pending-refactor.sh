#!/usr/bin/env bash
# next-pending-refactor.sh — print the first step that is green but not yet tidied.
#
# Reads a ledger (checkbox markdown) on stdin and writes the description of the FIRST
# `- [x]` step whose line ends in ` ⟂ refactor pending` — the mark tick-ledger.sh appends
# with the green commit — then exits 0. The mark is stripped, so what is printed is the
# same description next-unchecked.sh hands the loop and tick-criterion.sh matches on. If no
# step carries the mark it exits 3 with no output: every step that is green has also been
# tidied, so resume has nothing to re-enter.
#
# Usage:   next-pending-refactor.sh < .tdd/issue-<n>.md
set -euo pipefail

mark=' ⟂ refactor pending'
re="^[[:space:]]*- \[x\] (.*)${mark}$"

while IFS= read -r line || [[ -n "$line" ]]; do
  if [[ "$line" =~ $re ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    exit 0
  fi
done

exit 3

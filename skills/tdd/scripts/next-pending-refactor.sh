#!/usr/bin/env bash
# next-pending-refactor.sh — print the first step that is green but not yet tidied.
#
# Reads a ledger (checkbox markdown) on stdin and writes the description of the FIRST
# `- [x]` step lib/ledger.sh reports as refactor-pending — the mark tick-ledger.sh appends
# with the green commit — then exits 0. The mark is stripped, so what is printed is the
# same description next-unchecked.sh hands the loop and tick-criterion.sh matches on. If no
# step carries the mark it exits 3 with no output: every step that is green has also been
# tidied, so resume has nothing to re-enter.
#
# Usage:   next-pending-refactor.sh < .tdd/issue-<n>.md
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/ledger.sh"

pending_step=$'^[0-9]+\tdone\t[^\t]*\t1\t[^\t]*\t[^\t]*\t(.*)$'

while IFS= read -r record; do
  [[ "$record" =~ $pending_step ]] || continue
  printf '%s\n' "${BASH_REMATCH[1]}"
  exit 0
done < <(ledger_steps)

exit 3

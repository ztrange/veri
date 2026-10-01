#!/usr/bin/env bash
# tick-criterion.sh — tick one acceptance-criterion checkbox in an issue body.
#
# Pure text transform: reads the issue body on stdin and writes the updated body to
# stdout. Flips the FIRST unchecked GitHub task-list item ("- [ ]") whose text contains
# <matcher> (a literal substring; empty matcher matches the first unchecked box) to
# "- [x]". All other lines are passed through verbatim.
#
# Exit: 0 if a box was ticked, 3 if no unchecked box matched (body emitted unchanged).
#
# Usage: tick-criterion.sh <matcher>  < body.md > new-body.md
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/ledger.sh"

ledger_tick "${1:-}"

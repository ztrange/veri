#!/bin/sh
# tick-ledger.sh — check off one step in the local ledger, in place: a shim over veri/tick_ledger.py.
#
# Flips the first unchecked `- [ ]` step containing <matcher> to `- [x]`. --refactor-pending
# also appends the pending mark to that same line in the same write. Ticking a ⟦diff-checked⟧ step
# also runs tests-frozen.sh rerecord-earlier for it.
#
# usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase>] <ledger-file> <matcher>
# Exit:    0 a step ticked; 2 no <ledger-file>, it is a directory, the ledger could not be read, or the
#          ticked ledger could not be written — the file is left untouched — or, for a ⟦diff-checked⟧
#          tick, the re-record of earlier frozen records failed after the ledger was written; 3 no unchecked step matched —
#          the file is left untouched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/tick_ledger.py" "$@"

#!/bin/sh
# tick-ledger.sh — check off one step in the local ledger, in place: a shim over veri/tick_ledger.py.
#
# Flips the first unchecked `- [ ]` step containing <matcher> to `- [x]`. --refactor-pending
# also appends the pending mark to that same line in the same write.
#
# usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>
# Exit:    0 a step ticked; 1 the ledger could not be read; 2 no <ledger-file>, or the ticked
#          ledger could not be written — the file is left untouched; 3 no unchecked step matched —
#          the file is left untouched
exec python3 "$(dirname "$0")/veri/tick_ledger.py" "$@"

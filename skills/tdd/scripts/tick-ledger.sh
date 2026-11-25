#!/bin/sh
# tick-ledger.sh — check off one step in the local ledger, in place: a shim over veri/tick_ledger.py.
#
# Flips the first unchecked `- [ ]` step containing <matcher> to `- [x]`. --refactor-pending
# also appends the pending mark to that same line in the same write. Ticking a ⟦diff-checked⟧ step
# also runs tests-frozen.sh rerecord-earlier for it.
# Ticking an ⟦added⟧ step also ticks the first still-open line of equal step text (cut at ' ⟂ ') in
# issue-<n>-added.md, skipped when that file is missing.
#
# --surround-short <ledger-file> <matcher> appends ` ⟂ surround short` to the open legacy step whose next phase
# is surround, ticking nothing: exit 0 recorded, 1 the step already carries it (its one free relaunch of
# develop-surround is spent), 2 surround is not its next phase or the ledger is unreadable, 3 no step matched.
#
# usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --surround-short | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher>
# Exit:    0 a step ticked; 2 no <ledger-file>, it is a directory, the ledger could not be read, or the
#          ticked ledger could not be written — the file is left untouched — or, for a ⟦diff-checked⟧
#          tick, the re-record of earlier frozen records failed after the ledger was written, or, with --unpinnable/--already-holds, the --case never ran (ledger and
#          events untouched): its command exited 2, 126 or 127, 128 or above, or was killed by a signal; its file
#          path does not exist, or its output says no tests ran; or, run through make (the make test TESTS=<id>
#          fallback, or a one-test-file command whose first word is make), make's last stderr line is not a
#          top-level `make: *** [<target>] Error 1`, another `make: *** [<target>]` text ends in anything but
#          `Error 1`, or make's could-not-execute line sits just before it; 1 the case ran and fails; 3 no unchecked step matched —
#          the file is left untouched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/tick_ledger.py" "$@"

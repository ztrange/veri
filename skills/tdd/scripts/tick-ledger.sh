#!/bin/sh
# tick-ledger.sh — check off one step in the local ledger, in place: a shim over veri/tick_ledger.py.
#
# Flips the first unchecked `- [ ]` step containing <matcher> to `- [x]`. --refactor-pending
# also appends the pending mark to that same line in the same write. Ticking a ⟦diff-checked⟧ step
# also runs tests-frozen.sh rerecord-earlier for it.
# Ticking an ⟦added⟧ step also ticks the first still-open line of equal step text (cut at ' ⟂ ') in
# issue-<n>-added.md, skipped when that file is missing.
#
# usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher> (--unpinnable and --already-holds drop every mutation record whose named test is absent from the tree)
# Exit:    0 a step ticked; 2 no <ledger-file>, it is a directory, the ledger could not be read, or the
#          ticked ledger could not be written — the file is left untouched — or the step names a go-red
#          control (a before-state mutation probe of <sha>, or `the go-red control is <file> at <sha>`) and
#          `.tdd/issue-<n>-mutations.md` holds no `before <sha>` record for that sha nor a file/old/new
#          record for that file — the ledger is left unmodified — or, for a ⟦diff-checked⟧
#          tick, the re-record of earlier frozen records failed after the ledger was written, or a ⟦diff-checked⟧
#          step is ticked without a .tdd/pin-recheck-ok receipt whose sha resolves and differs from HEAD only under .tdd/
#          (the ledger is left untouched); 3 no unchecked step matched —
#          the file is left untouched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/tick_ledger.py" "$@"

#!/bin/sh
# add-ledger-step.sh — grow the plan while a run is under way: a shim over veri/add_ledger_step.py.
#
# Inserts each <text> as an unchecked step `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` on the lines
# after the step containing <anchor-substring>, or on the lines before it, in the order
# given. `instead-of` puts them where that step was and drops the step itself.
# VERI_STEP_GROWTH (default 5) caps how many ⟦added⟧ steps one ledger may hold, and the call is
# all or nothing: a batch that would exceed the cap inserts nothing and records every text as a
# plain bullet under `## Owed steps`. A <text> carrying ⟦ci-repair⟧ or ⟦suite-repair⟧ is inserted
# without ⟦added⟧ and never counts against the cap. The added step inherits the anchor's criterion,
# unless a leading --criterion <k> overrides it with criterion k.
#
# usage: add-ledger-step.sh [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]
# Exit:    0 inserted; 1 the batch would exceed VERI_STEP_GROWTH, owed instead;
#          2 a missing argument, an unknown position, an anchor matching no single step, a --criterion no ledger step carries,
#            or a bad VERI_STEP_GROWTH
exec python3 "$(dirname "$0")/veri/add_ledger_step.py" "$@"

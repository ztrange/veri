# Plan for #817 — tick-ledger, clear-refactor-pending and add-ledger-step never shorten the ledger silently

- [ ] tick-ledger.sh, when writing the ticked ledger fails, leaves the ledger file byte-identical to what it was and exits 2 ⟦criterion 1⟧
- [ ] clear-refactor-pending.sh, when writing the cleared ledger fails, leaves the ledger file byte-identical to what it was and exits 2 ⟦criterion 1⟧
- [ ] add-ledger-step.sh finds a last ledger step that has no trailing newline as its anchor, inserting after it and keeping it in the ledger, rather than exiting 2 with "anchor matches no single step" ⟦criterion 2⟧
- [ ] add-ledger-step.sh keeps a last line that has no trailing newline in the ledger after an insertion anchored on an earlier step ⟦criterion 2⟧
- [ ] add-ledger-step.sh counts a last line with no trailing newline that carries ⟦added⟧ against VERI_STEP_GROWTH, so a batch that only fits without it exits 1 and files the texts as owed ⟦criterion 2⟧
- [ ] add-ledger-step.sh's `## Owed steps` append after a last line with no trailing newline starts that heading on a line of its own, leaving the last line intact ⟦criterion 2⟧
- [ ] the suites of tick-ledger.sh, clear-refactor-pending.sh and add-ledger-step.sh pass, as part of the repository's full test command ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] no existing assertion in tick-ledger's, clear-refactor-pending's or add-ledger-step's suites (bash or pytest) changes, except one that pinned a defect criterion 1 or 2 fixes, changed only to the exit code, stderr or file state that criterion names ⟦diff-checked⟧ ⟦criterion 3⟧

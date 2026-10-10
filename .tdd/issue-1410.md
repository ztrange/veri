# Plan for #1410 — An exhausted contract phase filed as owed keeps its phase unmarked, so next-phase hands it back

- [x] `ledger-steps.sh next-phase` answers exit 3, printing no phase, on a ledger whose only open phased step carries ` ⟂ <phase> owed` on its contract phase — neither the owed contract phase nor any phase listed after it is handed back ⟦criterion 1⟧
- [x] A phased step whose contract phase is marked ` ⟂ <phase> owed` reads as `done` to `ledger-steps.sh`, and `next-unchecked.sh` skips it and hands over the next open step ⟦criterion 1⟧
- [x] `tick-ledger.sh --phase-owed <phase> <ledger> <matcher>` appends ` ⟂ <phase> owed` to the matching phased step's line, leaving its checkbox `[ ]`, its expand and migrate marks and every other line byte-identical; exit 2, ledger untouched, when the step does not list that phase or it is not the step's next unmarked phase ⟦criterion 1⟧
- [x] tick-ledger.sh's usage line, printed with exit 2 on a bad argument, names the `--phase-owed <phase>` flag beside `--phase <phase>` ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending
- [ ] Marking a contract phase owed leaves it visible as owed: the bullet under `## Owed steps` is unchanged, the step's line says `owed` and never ` ⟂ <phase> done`, and its checkbox stays `[ ]` ⟦criterion 2⟧
- [ ] On a ledger whose phased step has its contract filed under `## Owed steps` and marked owed, `ledger-steps.sh next-phase` and `next-unchecked.sh` run through their entry points both exit 3 ⟦criterion 3⟧
- [ ] `SKILL.md`'s exhausted-contract paragraph says to mark the contract phase owed with `tick-ledger.sh --phase-owed <phase>` before committing the ledger, pinned by a prose case ⟦criterion 3⟧

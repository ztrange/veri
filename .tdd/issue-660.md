# Plan for #660 — add-ledger-step.sh counts any line quoting the added mark against VERI_STEP_GROWTH, not only steps carrying the mark

- [x] a step line whose description quotes the added mark mid-text, but whose text does not end in that mark before any criterion mark, is not counted against VERI_STEP_GROWTH: with the budget at 1 and such a step in the ledger, inserting one step still exits 0 ⟦criterion 1⟧
- [x] a ticked step carrying the added mark whose line also ends in the refactor-pending mark is still counted against VERI_STEP_GROWTH: with the budget at 1 and one such step in the ledger, inserting one more exits 1 ⟦added⟧ ⟦criterion 1⟧
- [x] a step line whose text ends in the added mark, before its criterion mark, is still counted against VERI_STEP_GROWTH: with the budget at 1 and one such step in the ledger, inserting one more exits 1 and files it under Owed steps ⟦criterion 2⟧
- [x] steps carrying the ci-repair or suite-repair mark are still not counted against VERI_STEP_GROWTH, whether inserted or already in the ledger ⟦criterion 2⟧
- [x] lines outside the step checklist that quote the added mark, a bullet under the Owed steps heading and a prose line, are never counted against VERI_STEP_GROWTH ⟦criterion 3⟧ ⟂ refactor pending

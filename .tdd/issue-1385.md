# Plan for #1385 — tick-ledger.sh without --phase ticks a phased step [x], and the usage lines hide --phase and next-phase

- [x] tick-ledger.sh without --phase, whose matcher hits a step carrying ⟦phases: …⟧, exits 2 with a stderr line naming --phase and leaves the ledger byte-identical, while a step without phases still ticks [x] exactly as before ⟦criterion 1⟧
- [x] tick-ledger.sh given both --phase <p> and --refactor-pending, in either order, is refused with exit 2 and a stderr line naming both flags, leaving the ledger byte-identical ⟦criterion 2⟧
- [x] the usage line tick-ledger.sh prints on a bad argument names --phase <phase> ⟦criterion 3⟧ ⟂ refactor pending
- [ ] the usage line ledger-steps.sh prints on a bad argument names next-phase ⟦criterion 3⟧

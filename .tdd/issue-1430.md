# Plan for #1430 — tick-ledger.sh --phase-owed accepts an expand or migrate phase, which ends the step early

- [ ] tick-ledger.sh --phase-owed with a phase other than contract-a or contract-b (expand or migrate) exits 2, leaves the ledger byte-identical, and names that phase in its refusal on stderr, while --phase-owed contract-a and contract-b still mark the phase owed as today ⟦criterion 1⟧

# Plan for #3338 — reorder-ledger-steps.sh docs say the step is committed, but the script never commits

- [ ] ⟦skill-edit⟧ skills/tdd/SCRIPTS.md: the reorder-ledger-steps.sh row and SC19 say the script only rewrites the ledger and never commits, the caller commits it in a plan: commit, as the issue's ## Requirements row SC19<reword> states ⟦criterion 1⟧
- [ ] The header of skills/tdd/scripts/reorder-ledger-steps.sh states "does not commit" next to its Exit line, pinned by a small case on the shim's header text and no production change beyond that header ⟦criterion 2⟧

# Plan for #4709 — A Red/Green step whose prose quotes a kind mark (`⟦diff-checked⟧`) is routed to that kind, since red_half.refused tests by substring

- [x] `red_half.refused` returns no kind for a step that only quotes a `red_half.REFUSED` mark in backticked prose, and still returns it from the step's trailing marker run, one case per mark ⟦criterion 1⟧
- [ ] `run-step.sh` routes a step that only quotes `⟦diff-checked⟧` in its prose to `red-half.sh`, not `diff-step.sh` ⟦criterion 2⟧
- [ ] `red_half.refused` and `ledger.ledger_steps` agree on the kind of every step of a fixture ledger mixing quoted and trailing marks ⟦criterion 3⟧

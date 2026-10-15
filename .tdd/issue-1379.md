# Plan for #1379 — SKILL.md: a malformed add-ledger-step.sh --criterion bail names no cause token

- [x] `classify-bail.sh step-add-refused` prints `system` and exits 0 — the cause an `add-ledger-step.sh` exit 2 bails with is one classify-bail.sh knows, as a system failure ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `SKILL.md` says, at every call site of `add-ledger-step.sh` (the over-budget split, the Green `SPLIT:`, the refactor PASS growth, the suite-repair step, the CI-repair steps and the revise-exhausted split), that its exit 2 bails with cause `step-add-refused`, and *Bailing*'s cause list names `step-add-refused` as a **system** failure ⟦criterion 1⟧

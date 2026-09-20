# Plan for #363 — Green may SPLIT a too-big step into smaller steps before it

- [x] `classify-bail.sh step-too-big` prints `process` on stdout and exits 0 ⟦criterion 5⟧
- [x] The prompt `build-develop-prompt.sh green …` builds lets the leaf report one to three `SPLIT: <behaviour-level criterion>` lines instead of an implementation, changing no production code ⟦criterion 1⟧
- [ ] The prompt `build-develop-prompt.sh revise green …` builds offers the same `SPLIT:` report ⟦criterion 2⟧
- [ ] SKILL.md's Green section, on `SPLIT:`, restores the tree to `HEAD`, adds the split steps before STEP in one `add-ledger-step.sh` call, commits the ledger, emits `step-split` and returns to `next-unchecked.sh` ⟦criterion 3⟧
- [ ] SKILL.md bails with cause `step-too-big` when `add-ledger-step.sh` exits 1 on a split, and its Bailing section lists that cause as a process failure ⟦criterion 4⟧

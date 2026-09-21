# Plan for #194 — Resume only resets a dirty tree for a pending refactor, so a killed Red or Green leaf's work survives — and can deadlock the Draft PR step

- [x] Resume resets a dirty worktree before it asks for a pending refactor, so a resume with no step carrying the refactor-pending mark still discards the stray work ⟦criterion 1⟧
- [x] Resume captures the dirty paths before the reset and names them in the `### ▶️ Resuming` comment ⟦criterion 2⟧
- [ ] The Draft PR step's refusal names a remedy that applies with a dirty tree, no pending step and no unchecked step, and the run reaches the PR after it ⟦criterion 3⟧
- [ ] The Resume section states that a killed Red or Green leaf leaves the same stray work a killed refactor leaf does ⟦criterion 4⟧

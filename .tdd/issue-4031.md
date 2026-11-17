# Plan for #4031 — PRD 027.9: the Draft PR step's sub-step 1 is one call

- [x] `pr-prepare.sh <n>` follows the port convention, refuses no argument and a missing input with exit 2, and stops at a dirty tree or a refactor-pending step with exit 1 ⟦criterion 1⟧ ⟦criterion 12⟧
- [x] it rebases, runs the regrade block, the rebased tip's suite when owed, the tree check and the pinned-lease push, then the refactor-owed list and its skip event, and settles `.tdd/issue-<n>-pr-prepare` ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 9⟧ ⟦criterion 10⟧ ⟦criterion 11⟧
- [x] a wait whose slice runs out exits 3 and a second call only waits again; its wait record names its conductor ⟦criterion 8⟧
- [ ] a guard fails when an inner call is a `$S/` script sub-step 1 does not name, and the rebase and pinned-lease push are made for real ⟦criterion 13⟧
- [ ] docs: sub-step 1's opening, `SCRIPTS.md`, rows and grades ⟦criterion 14⟧

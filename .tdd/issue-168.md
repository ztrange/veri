# Plan for #168 — A step's end ticks an issue criterion that later steps still have to build

Notation: a step serving the issue's k-th acceptance criterion (1-based, in the order of the issue body's `## Acceptance criteria` checkboxes) ends in ` ⟦criterion k⟧`, before any ` ⟂ refactor pending` mark; a gap step carries no such token.

- [x] Given a ledger where two steps carry ` ⟦criterion k⟧` for the same k and only the first is ticked with no refactor-pending mark, a criterion-finished script exits 3 for criterion k; once both are ticked with no ` ⟂ refactor pending` mark it exits 0 ⟦criterion 1⟧
- [x] A ticked step that carries no ` ⟦criterion k⟧` token makes no criterion finished: for a criterion no step serves, the criterion-finished script exits 3 even when every step in the ledger is ticked and verified ⟦criterion 2⟧
- [x] `next-unchecked.sh`, `next-pending-refactor.sh`, `tick-ledger.sh` and `clear-refactor-pending.sh` each have a suite case on a ledger whose steps carry the ` ⟦criterion k⟧` notation, matching and printing step text exactly as they do without it ⟦criterion 4⟧
- [x] `SKILL.md`'s *Step done* and pin paths run the criterion-finished script and tick the issue criterion only on its exit 0, posting `### ✅ Step done` and ticking nothing on exit 3 ⟦criterion 3⟧
- [ ] `SKILL.md` step 2's plan-writing guidance tells the conductor to end each ledger step with ` ⟦criterion k⟧` for the criterion it serves, and to leave a gap step without one ⟦criterion 3⟧

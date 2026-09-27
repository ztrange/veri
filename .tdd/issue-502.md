# Plan for #502 — every refactor pass is recorded per pass, not last-write-wins

- [x] SKILL.md's `refactor` mark carries a pass index `pass=<k>`: 1 for a step's first refactor pass, and one more each time the triangulation path resumes the refactor loop and reaches the refactor sub-step again
- [x] metrics.sh renders a per-pass section keyed by step and pass: a step whose log carries two `refactor` marks (pass=1 and pass=2) shows two rows, each with its own transforms against budget and its own stop reason ⟦criterion 1⟧
- [x] A step whose log carries one `refactor` mark (with or without a `pass=` key) renders as it does today: its By-step row keeps the same refactor and stopped cells, and it appears once in the per-pass section ⟦criterion 2⟧
- [x] Each per-pass row carries that pass's verify-refactor verdict, the wall seconds and the cost of that pass's refactor-phase leaves ⟦criterion 3⟧
- [x] Each per-pass row carries its own verdict, wall seconds and cost on a log in the order SKILL.md writes it: that pass's refactor leaf, then its verify-refactor verdict, then the conductor's `refactor` mark for the pass ⟦added⟧ ⟦criterion 3⟧
- [x] Each per-pass row carries the count of refactor-phase revises spent in that pass
- [x] On a log in the order SKILL.md writes it — a pass's first verify-refactor verdict, then its `refactor` mark, then that pass's revise loop (revise marks, revise-refactor leaves, re-verify verdicts) — the revises, the wall seconds and the cost of that revise loop count toward that pass and not the next one, and the pass's verdict is its last verify-refactor verdict ⟦added⟧
- [ ] The per-pass section is part of metrics.sh's `### 📊 Metrics` block whichever mark ended the run — done, bail or stop — so it reaches the issue thread with the rest of the metrics ⟦criterion 4⟧
- [ ] No existing table's key column or column names change, and the per-pass section adds no column named `kind` (prose says run kind) ⟦criterion 5⟧

# Plan for #360 — ledger step growth: add-ledger-step.sh and its budget

- [x] add-ledger-step.sh inserts `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` after the anchor step, carrying the anchor's k, exit 0 ⟦criterion 1⟧
- [x] `before` inserts several texts, in the order given, on the lines before the anchor step ⟦criterion 2⟧
- [x] an anchor step carrying no `⟦criterion k⟧` yields an added step carrying none ⟦criterion 3⟧
- [x] criterion-finished.sh does not report k finished while an unchecked `⟦added⟧` step serving k remains ⟦criterion 4⟧
- [x] over budget, the call inserts no checkbox, exits 1, and appends every text as a plain bullet under a trailing `## Owed steps` heading ⟦criterion 5⟧
- [x] next-unchecked.sh never returns a bullet under `## Owed steps` ⟦criterion 6⟧
- [x] an anchor matching no step, or more than one, exits 2 and leaves the ledger byte-identical ⟦criterion 7⟧
- [x] VERI_STEP_GROWTH unset allows 3 added steps; a value that is not a non-negative integer, set-but-empty included, exits 2 and leaves the ledger byte-identical ⟦criterion 8⟧
- [x] SKILL.md's preflight refuses to start on a bad VERI_STEP_GROWTH, as it does a bad VERI_REFACTOR_BUDGET ⟦criterion 9⟧
- [x] SKILL.md's Draft PR section copies the ledger's `## Owed steps` bullets into the PR body under `## Owed steps` ⟦criterion 10⟧
- [x] SKILL.md says each insertion emits a `step-added` event ⟂ refactor pending
- [ ] CLAUDE.md's budgets invariant names VERI_STEP_GROWTH as a fifth axis, plan growth, never merged with the other four ⟦criterion 11⟧

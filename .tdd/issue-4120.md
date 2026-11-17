# Plan for #4120 — PRD 032.9: a run fixes the weak and coupled cases it reported, each proven by a flip

- [x] `VERI_TEST_QUALITY_FIXES` is a `tunables.TABLE` entry, a whole number, default 1, and `run-conductor.sh` given any other value exits 2 before preflight naming it and its value ⟦criterion 1⟧
- [x] `build-develop-prompt.sh diff` for a `⟦test-quality⟧` step renders `prompts/_develop-diff-test-quality.md`, and for a step without it does not ⟦criterion 2⟧
- [ ] `_develop-diff-test-quality.md`, `DRAFT-PR.md`'s appended steps and `### Test quality` marks, `DIFF-CHECKED.md`'s flip and `CLAUDE.md`'s budgets invariant, graded ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 6⟧

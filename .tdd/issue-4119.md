# Plan for #4119 — PRD 032.5: a run reports the weak, redundant and coupled cases among the tests it touched

- [x] `build-develop-prompt.sh test-quality <spec> <test-cmd> <test-file>…` renders `prompts/develop-test-quality.md`, holding `SMELLS.md`'s test-code rules and the given test files; a phase it did not accept before ⟦criterion 1⟧
- [x] `develop-test-quality` resolves to `VERI_MODEL_DEVELOPER`, else `VERI_MODEL`, with no knob of its own ⟦criterion 2⟧
- [ ] `test-quality.sh record <n> < <report>` writes `.tdd/issue-<n>-test-quality.md` with each `FINDING:` line's finding and exits 0 ⟦criterion 3⟧
- [ ] `test-quality.sh record` exits 3 on `FINDING: none`, the file written with no finding ⟦criterion 4⟧
- [ ] `test-quality.sh record` exits 2, writing nothing, on a line naming no `::` case, a case its file does not define, or no `FINDING:` line ⟦criterion 5⟧
- [ ] `prompts/develop-test-quality.md`, `DRAFT-PR.md` sub-step 1 and the PR body section, and `SCRIPTS.md`'s `test-quality.sh` entry, graded ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧

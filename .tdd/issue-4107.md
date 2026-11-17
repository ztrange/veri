# Plan for #4107 — PRD 031.1b: a confirmed region is surrounded under a blind verifier

- [x] `build-develop-prompt.sh surround` renders `prompts/develop-surround.md`, and `revise surround` is accepted ⟦criterion 1⟧
- [x] `build-verify-prompt.sh surround` renders `prompts/verify-surround.md` from the `pin` phase's inputs and exits 2 on any other ⟦criterion 2⟧
- [x] `tick-ledger.sh --phase surround` records `⟂ surround done` after `⟂ seam done`, and `ledger-steps.sh next-phase` then exits 3 ⟦criterion 3⟧
- [x] a run started with `VERI_SKIP_VERIFY=surround` exits 2 before its baseline ⟦criterion 4⟧
- [x] `classify-bail.sh surround-owed` still prints `process` ⟦criterion 5⟧
- [x] docs: `develop-surround.md`, `verify-surround.md`, `LEGACY.md`, CLAUDE.md, SKILL.md sentence, CONTEXT.md, rows and grades ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧

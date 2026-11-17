# Plan for #4106 — PRD 031.1a: a `legacy` issue names a region, and its seam is confirmed or refused

- [x] capture writes a `## Legacy` section for a `legacy`-labelled issue ⟦criterion 1⟧
- [x] capture refuses an issue labelled both `legacy` and `refactor`, exit 2, naming both labels ⟦criterion 1⟧
- [x] `classify-bail.sh no-seam` and `classify-bail.sh surround-owed` print `process` ⟦criterion 9⟧
- [ ] `build-verify-prompt.sh plan` fills `{{LEGACY_PLAN}}` with `_verify-plan-legacy.md` for a `## Legacy` spec, nothing otherwise ⟦criterion 4⟧
- [ ] `build-develop-prompt.sh seam` renders `prompts/develop-seam.md` ⟦criterion 6⟧
- [ ] `seam-outcome.sh` reads a develop-seam report: yes+SEAM exit 0, no exit 1 with the reason, unreadable exit 2 ⟦criterion 7⟧
- [ ] `tick-ledger.sh --phase seam` records `⟂ seam done` and `ledger-steps.sh next-phase` then prints `surround` ⟦criterion 11⟧
- [ ] `affected-suites.sh` over a change to only `skills/tdd/LEGACY.md` selects the files naming it, no widening ⟦criterion 13⟧
- [ ] docs: `_verify-plan-legacy.md`, `develop-seam.md`, `LEGACY.md`, `BAIL.md`, SKILL.md sentence, CLAUDE.md, CONTEXT.md, rows and grades ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 5⟧ ⟦criterion 8⟧ ⟦criterion 10⟧ ⟦criterion 12⟧ ⟦criterion 14⟧

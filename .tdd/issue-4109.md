# Plan for #4109 — PRD 031.3a: the coverage issue a refusing refactor files is a `legacy` issue

- [x] `coverage-blocker.sh <n>` labels the coverage issue `legacy` beside the opt-in label and `filed-by:<lane>` ⟦criterion 1⟧
- [x] with no `legacy` label in the repo it files without it, writes the one stderr line and still blocks #<n>; a label check with no answer exits 2 before filing ⟦criterion 2⟧
- [x] the body has a `## Region` section holding `ledger-steps.sh current-or-last-done`'s line; an unreadable ledger or none exits 2 before filing ⟦criterion 3⟧
- [x] an issue already open with the title is reused unrelabelled, title and `MUTATION:` criteria unchanged ⟦criterion 4⟧
- [x] docs: `LEGACY.md` seeds the mutant table from `MUTATION:` criteria, `REFACTOR-KIND.md` says the issue is `legacy`, rows and grades ⟦criterion 5⟧ ⟦criterion 6⟧

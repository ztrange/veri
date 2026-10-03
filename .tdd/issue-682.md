# Plan for #682 — SKILL.md reads the current step, the last done step and criterion k through ledger-steps.sh verbs instead of inline pipelines

- [x] `ledger-steps.sh` run with no argument prints exactly the tab-separated `ledger_steps` records it prints today, for every step kind and mark ⟦criterion 1⟧
- [x] `ledger-steps.sh current` prints the text of the first refactor-pending step when one exists, else of the first open `step`-kind step (what `next-unchecked.sh` would print, skipping `⟦full-suite⟧` and `⟦human-owed⟧`), and exits 3 with no output when neither exists ⟦criterion 2⟧
- [x] `ledger-steps.sh last-done` prints the text of the last done step with ` ⟂ refactor pending` cut, and exits 3 with no output when no step is done ⟦criterion 3⟧
- [x] `ledger-steps.sh last-done` counts a done step whose text is empty as done: when it is the last done step it prints an empty line and exits 0, not exit 3 ⟦added⟧ ⟦criterion 3⟧
- [x] `ledger-steps.sh criterion <k>` reading an issue body on stdin prints the text of the k-th checkbox under `## Acceptance criteria` only, never a checkbox from another section, and exits 3 with no output when that section has fewer than k checkboxes ⟦criterion 4⟧
- [x] `ledger-steps.sh` given an unknown verb, or `criterion` with a missing or non-integer `<k>`, prints a usage line on stderr and exits 2 ⟦criterion 5⟧
- [x] `ledger-steps.sh criterion <k>` reads a `<k>` with leading zeros in base 10: `criterion 08` prints the 8th acceptance-criterion checkbox, or exits 3 with no output when there are fewer than 8, never failing with a bash arithmetic error ⟦added⟧ ⟦criterion 5⟧
- [ ] SKILL.md's leaf and verifier launch lines read the step through `ledger-steps.sh current`, and a step title carrying `$`, a backtick or a double quote reaches the leaf's `VERI_STEP` and the verifier's `--step` byte-identical ⟦criterion 6⟧
- [ ] SKILL.md spells none of the three inline pipelines — the `|| next-unchecked.sh` current-step read, the `tail -1 | cut -f7-` last-done read and the `sed -n '<k>p'` criterion read — calling `ledger-steps.sh current`, `last-done` and `criterion <k>` instead, and the prose suites that pinned them follow ⟦criterion 7⟧
- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 8⟧

# Plan for #3917 — PRD 029.3: an exhausted leaf can answer "a test-only step ahead"

- [x] after a reroute, a `CONTRADICTS:` case two test files define makes `wrong-test-route.sh` exit 2 with empty stdout and one stderr line naming the case and both files, no `TypeError` ⟦criterion 1⟧
- [x] `exhausted-outcome.sh --step-ahead <red-test-id>` prints one `prep <file>::<case> …` line naming each `STEP_AHEAD:` case its file defines and exits 0 ⟦criterion 2⟧
- [x] `exhausted-outcome.sh --step-ahead <red-test-id>` skips a `STEP_AHEAD:` line naming the red case and exits 3 printing nothing when no line remains ⟦criterion 3⟧
- [x] `exhausted-outcome.sh --step-ahead <red-test-id>` exits 2 with empty stdout and a stderr line naming the line when a `STEP_AHEAD:` value has no `::` ⟦criterion 4⟧
- [x] `exhausted-outcome.sh --step-ahead <red-test-id>` exits 2 with empty stdout and a stderr line naming the line when a `STEP_AHEAD:` value names no existing file ⟦criterion 4⟧
- [x] `exhausted-outcome.sh --step-ahead <red-test-id>` exits 2 with empty stdout and a stderr line naming the line when a `STEP_AHEAD:` value names a case its file does not define ⟦criterion 4⟧
- [x] run without `--step-ahead`, `exhausted-outcome.sh` prints and exits as today on input holding `STEP_AHEAD:` lines, alone and beside `SPLIT:` or `NEEDS_USER:` lines ⟦criterion 5⟧
- [ ] `JOURNAL.md`'s `reroute` row lists the `at` field ⟦criterion 6⟧
- [ ] `prompts/develop-exhausted.md` offers and declares `STEP_AHEAD:`, graded PASS against rows XH9 to XH11 ⟦criterion 7⟧
- [ ] `REVISE.md`'s exhausted section runs `--step-ahead` on the plain read's exit 3, graded PASS against rows RV66 and RV67 ⟦criterion 8⟧
- [ ] `SCRIPTS.md` has an `$S/exhausted-outcome.sh` entry, graded PASS against row SC140 ⟦criterion 9⟧

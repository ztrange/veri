# Plan for #595 — #496 follow-ups: two model-knobs-recorded cases changed meaning, harness sourced twice, suite event logs committed to skills/

- [x] after `lib/harness.sh` is sourced, a `scratch_dir` and an `on_exit` are registered, and `lib/harness.sh` is sourced again, exiting the shell removes that scratch directory, runs that `on_exit` command exactly once and leaves no scratch list file behind — a case in `unit/harness.test.sh` plants this double source ⟦criterion 5⟧
- [x] sourcing `lib/harness.sh` a second time keeps the `pass`/`fail` counts already reached ⟦criterion 6⟧
- [x] `unit/no-report-copies.test.sh` admits a counter-initialisation hit only through an exemption entry that names the file, matches the line by its text rather than its number, and carries a reason; a hit no entry matches is still flagged, naming the file and line ⟦criterion 8⟧
- [x] `unit/no-report-copies.test.sh` goes red, naming the file and line, on a planted suite line `pass=0; fail=0` and on one `pass="${pass:-0}"`, still goes red on `pass=0 fail=0`, and stays green on the tree ⟦criterion 7⟧ ⟂ refactor pending
- [ ] `model-knobs-recorded.test.sh` carries no line the counter-initialisation audit flags (the `:106` and `:140` resets are gone) and no exemption entry names it, with its probes still passing ⟦criterion 8⟧
- [ ] the widened audit still flags neither `lib/harness.sh` nor `unit/harness.test.sh` ⟦criterion 9⟧
- [ ] the `model-knobs-recorded.test.sh` case that checks each suite ends in a bare `finish` line is named for that — each suite ends in the harness's `finish` — and no longer claims each suite prints its own count line ⟦criterion 2⟧
- [ ] the `model-knobs-recorded.test.sh` check that each suite sources `lib/harness.sh` is a case named for that, and no case name claims the four suites keep their own counters ⟦criterion 3⟧
- [ ] the plain-shell probe sources `record-helpers.sh` in a shell that has not sourced `lib/harness.sh`, asserts the full set of functions that defines, and its case name no longer claims `record-helpers.sh` defines only the five helpers ⟦criterion 4⟧
- [ ] CLAUDE.md's "Testing idiom" section says the rule that the four `-recorded` suites keep their own counters (#225) was retired by #496, naming `record-helpers.sh` and `lib/harness.sh` ⟦criterion 1⟧

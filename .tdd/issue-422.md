# Plan for #422 — a pipefail suite reads its writer's SIGPIPE as the answer

- [x] A guard names `<suite>:<line>` and fails the run when a suite that declares `pipefail` ends a pipeline in `grep -*q` ⟦criterion 2⟧
- [x] The same guard also names a pipeline that ends in `head` ⟦criterion 2⟧
- [x] The guard exempts a site listed in an exemption table carrying a reason per entry, and refuses an entry whose reason is missing ⟦criterion 2⟧
- [x] A planted offender turns the guard red naming it, and the guard is green again once the plant is removed ⟦criterion 3⟧
- [x] `prompt-test-tiers.test.sh`'s prompt probes give the same verdict on a matching and a non-matching prompt whether or not the writer is preempted ⟦criterion 1⟧
- [x] `count-line-guard.test.sh`'s pipeline-fed matches give the same verdict on a matching and a non-matching input whether or not the writer is preempted ⟦criterion 1⟧
- [x] Every remaining site the guard names is repaired or exempted, so the guard passes over the whole tree as it stands ⟦criterion 4⟧
- [ ] the guard names a site whose pipeline is split across lines — the `|` ending one line and the early-exiting reader opening the next — so a suite that declares `pipefail` cannot escape it by wrapping ⟦added⟧ ⟦criterion 4⟧
- [ ] the guard's roster case says what it found when `make -n test` names no suite, instead of failing the run — so a tree that has no Makefile (every scratch plant `sigpipe-guard.test.sh` builds) gets the guard's real verdict ⟦added⟧ ⟦criterion 4⟧
- [ ] `CLAUDE.md`'s testing idiom section states the pipefail/SIGPIPE rule once ⟦criterion 5⟧

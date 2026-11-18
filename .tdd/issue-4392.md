# Plan for #4392 — PRD 038.8: pr-checks.sh runs the Draft PR checks between pr-prepare and readying in one call

- [x] pr-checks.sh <n> (a shim over veri/pr_checks.py) exits 2 on bad arguments, a missing .tdd/issue-<n>-preflight or ledger, naming it, before any call ⟦criterion 5⟧
- [x] a clean run makes, in order, the lint run (its `lint` event and `### Lint` section), the test-quality check (the empty record on test-quality.sh files exit 3), red-setup.sh worst, coupling.sh, refactor-candidates.sh and unwired.sh with DRAFT-PR.md's arguments, one line per call with its exit code and never .tdd/lint.out's text ⟦criterion 1⟧
- [x] a clean run settles .tdd/issue-<n>-pr-checks with the candidates url, launching no leaf, appending no ledger step, committing, pushing and readying nothing and running no metrics.sh ⟦criterion 4⟧
- [x] test-quality.sh files exit 0 stops it with exit 1 at test-quality before the develop-test-quality launch ⟦criterion 2⟧
- [x] a non-zero lint writes its event and its `### Lint` section with the output's last 20 lines cut at 300 characters, then stops it with exit 1 at lint, appending no repair step ⟦criterion 2⟧
- [x] a coupling.sh pair writes the `### Coupling` section, then stops it with exit 1 at coupling, recording no row ⟦criterion 2⟧
- [x] an unwired.sh finding stops it with exit 1 at unwired, writing no pending record and no bail ⟦criterion 2⟧
- [x] a lint wait whose slice runs out exits 3 with .tdd/issue-<n>-pr-checks-wait, and a second call by the same conductor only waits again, starting no second lint ⟦criterion 3⟧
- [x] a record holding a weak-assertion or implementation-coupled finding the VERI_TEST_QUALITY_FIXES budget still owes a step stops it with exit 1 at test-quality
- [x] no `veri: lint:` line skips the lint; a lint command that cannot be read, one stopped past VERI_LINT_TIMEOUT and one that recorded no exit each write their `### Lint` sentence and go on, and a stop request of `now` stops it at lint
- [x] coupling.sh exit 3 that drops a stale coupling row stops it with exit 1 at coupling, leaving the commit to the conductor
- [x] every inner call that obtains no answer (the default branch, git merge-base, test-quality.sh files, red-setup.sh worst, coupling.sh, refactor-candidates.sh, unwired.sh, event.sh) stops it with exit 2
- [ ] the pr-checks.sh shim runs the module: its usage and exit 2 with no argument, and exit 2 naming a missing preflight
- [ ] DRAFT-PR.md sub-step 1 names $S/pr-checks.sh <n> after pr-prepare.sh, SCRIPTS.md and veri/README.md list it, and a guard fails when pr_checks.CALLS names a script sub-step 1 does not ⟦criterion 6⟧

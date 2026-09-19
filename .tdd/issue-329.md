# Plan for #329 — make profile ranks make test's cases by wall time so a slow one is found without guessing

- [x] Given a fixture suite whose trace carries fabricated EPOCHREALTIME timestamps for two cases, one above and one below VERI_PROFILE_THRESHOLD, only the case at or above it is printed ⟦criterion 3⟧ ⟂ refactor pending
- [ ] The printed line for a fixture case matches `<secs> <suite> case <n> L<a>-<b>` exactly, with n and the line range matching the fixture's own case number and source lines ⟦criterion 5⟧
- [ ] A case boundary is a top-level pass=/fail= assignment whose value exceeds the counter's previous value, and no other assignment (a top-level pass=0 plus a local passed=1 inside a case is not two boundaries) ⟦criterion 4⟧
- [ ] Cases at or above the threshold are printed slowest first, proven with three fixture cases of distinct fabricated durations ⟦criterion 6⟧
- [ ] Setting VERI_PROFILE_THRESHOLD to a different value changes which fixture cases are printed, against the same injected timestamps ⟦criterion 7⟧
- [ ] A non-numeric VERI_PROFILE_THRESHOLD, and a suite whose trace never shows a pass=/fail= increment, both exit 2 ⟦criterion 8⟧
- [ ] With VERI_PROFILE_THRESHOLD unset the threshold is 1 second, and a run in which no case reaches the threshold still exits 0
- [ ] make -n profile runs every suite make -n test runs, over the same TESTS glob and the same offline/PATH environment test's recipe sets up ⟦criterion 1⟧
- [ ] make -n test does not invoke profile and profile does not invoke test — they are independent targets ⟦criterion 2⟧
- [ ] profile.test.sh requests no real sleep and runs no real suite from skills/tdd/scripts/tests/ — only its own fixture suites — and is covered by make test's own glob ⟦criterion 9⟧

# Plan for #285 — VERI_NEW_SKILL=1 leaks from a conductor launch into the suites the run executes, failing run-conductor.test.sh 3/22

- [x] run-conductor.test.sh gives the same result with VERI_NEW_SKILL=1 ambient in its caller's environment as with it unset (22 passed, 0 failed both ways) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] run-conductor.sh does not hand VERI_NEW_SKILL to the nested claude -p conductor: a launch made with VERI_NEW_SKILL=1 re-pins as documented, yet the conductor process it starts sees no VERI_NEW_SKILL in its environment
- [ ] hermetic-suites.test.sh has a same_both_ways case that runs run-conductor.test.sh with and without an ambient VERI_NEW_SKILL=1 and fails if the two results differ ⟦criterion 2⟧

# Plan for #4453 — PRD 036.5: a fixed N narrows T to what it needs

- [ ] the hermetic fixture points VERI_TEST_BUDGET_DIR at the case's tmp_path, and the process cases that hand a leg the ceiling and cap files hand it the budget directory too
- [ ] with one unexpired entry under VERI_TEST_BUDGET_DIR, the leg's T is max(2, min(C, S)); with none it is C ⟦criterion 3⟧
- [ ] an unreadable, malformed or expired entry adds nothing and fails nothing, and an expired one is removed ⟦criterion 3⟧
- [ ] a waiting leg reads T again on every pass of its wait loop, so a T widened while it waits lets it start ⟦criterion 4⟧
- [ ] a T narrowed below what a running leg holds leaves that leg's registry entry as it was ⟦criterion 5⟧
- [ ] when S narrows T below C, the wait line names each entry's lane and need beside C and C's source ⟦criterion 6⟧
- [ ] with VERI_PYTEST_WORKERS exported the leg reads no entry, and test-ceiling.sh neither reads nor writes one ⟦criterion 8⟧
- [ ] dispatch.sh refuses a VERI_CONDUCTOR_TEST_WORKERS that is not a whole number of at least 1, exit 2 naming it, before any poll ⟦criterion 2⟧
- [ ] dispatch.sh writes its lane's need, max(N, live conductors) × d, and its expiry to its lane's entry at every poll, replaced whole through a temporary file ⟦criterion 1⟧
- [ ] role-state.sh dev set n <k> writes the lane's entry and prints N, the lane's need, the other lanes' needs, C with its source and the T a leg would read now ⟦criterion 7⟧
- [ ] vdev's The slot decision, CLAUDE.md's Testing idiom and SCRIPTS.md's dispatch.sh and role-state.sh entries state the budget, regraded ⟦criterion 9⟧ ⟦criterion 10⟧ ⟦criterion 11⟧

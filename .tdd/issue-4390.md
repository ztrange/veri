# Plan for #4390 — PRD 038.7: pr-prepare.sh commits its regrade under a fixed subject and slices it with exit 3

- [x] the regrade block runs through detach-command.sh start and wait: a wait whose slice runs out exits 3 with the wait record, and a second call by the same conductor only waits again, regrading nothing twice ⟦criterion 3⟧
- [ ] with no rebase it commits exactly the GRADED files the regrade block modified as `docs: regrade the prose the branch signed (#<n>)` before its exit, and none when it modified none ⟦criterion 1⟧
- [ ] after a rebase the regrade commit is made before the pinned-lease push, so the tree is clean on exit 0 on both paths ⟦criterion 2⟧
- [ ] DRAFT-PR.md sub-step 1 and SCRIPTS.md's pr-prepare.sh entry name the commit, its subject and the detached regrade, graded by DP354 and SC586; SKILL.md unchanged ⟦criterion 4⟧

# Plan for #775 — veri's exit-code contract holds in tick-issue-criterion, refactor-overflow, wait-ci and workqueue

- [ ] tick-issue-criterion.sh, when gh fails on the body edit with any non-zero status (1, 3 and 5 alike), exits 2 and the issue body is left unchanged ⟦criterion 1⟧
- [ ] refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧
- [ ] wait-ci.sh given a non-numeric slice or a non-numeric total exits 2 and names the bad argument on stderr, never 1 ⟦criterion 3⟧
- [ ] workqueue.sh with a missing worker, a missing issue or a missing park reason exits 2 with its usage text on stderr and leaves no .tdd/workqueue.tmp.* file ⟦criterion 4⟧
- [ ] no assertion of a case the four scripts' existing suites already held is changed by this branch ⟦diff-checked⟧ ⟦criterion 5⟧
- [ ] every case the four scripts' existing suites hold passes ⟦full-suite⟧ ⟦criterion 5⟧

# Plan for #775 — veri's exit-code contract holds in tick-issue-criterion, refactor-overflow, wait-ci and workqueue

- [x] tick-issue-criterion.sh, when gh fails on the body edit with any non-zero status (1, 3 and 5 alike), exits 2 and the issue body is left unchanged ⟦criterion 1⟧
- [x] refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧ ⟂ refactor pending
- [ ] wait-ci.sh given a non-numeric slice or a non-numeric total exits 2 and names the bad argument on stderr, never 1 ⟦criterion 3⟧
- [ ] workqueue.sh with a missing worker, a missing issue or a missing park reason exits 2 with its usage text on stderr and leaves no .tdd/workqueue.tmp.* file ⟦criterion 4⟧
- [ ] no assertion of a case the four scripts' existing suites already held is changed by this branch, except the three the 2026-10-04 amendment names (refactor-overflow.test.sh:299 and the ("1", 1, 1, …) and ("1", 4, 4, …) rows of test_refactor_overflow.py), which change to expect exit 2 and nothing else ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 5⟧
- [ ] every case the four scripts' existing suites hold passes ⟦full-suite⟧ ⟦criterion 5⟧

# Plan for #775 — veri's exit-code contract holds in tick-issue-criterion, refactor-overflow, wait-ci and workqueue

- [x] tick-issue-criterion.sh, when gh fails on the body edit with any non-zero status (1, 3 and 5 alike), exits 2 and the issue body is left unchanged ⟦criterion 1⟧
- [x] refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧
- [x] wait-ci.sh given a non-numeric slice or a non-numeric total exits 2 and names the bad argument on stderr, never 1 ⟦criterion 3⟧ ⟂ refactor pending
- [ ] workqueue.sh with a missing worker, a missing issue or a missing park reason exits 2 with its usage text on stderr and leaves no .tdd/workqueue.tmp.* file ⟦criterion 4⟧
- [ ] no assertion of a case the four scripts' existing suites already held is changed by this branch, except those the issue's 2026-10-04 amendment names (refactor-overflow.test.sh:299; the ("1", 1, 1, …) and ("1", 4, 4, …) rows of test_refactor_overflow.py; test_wait_ci.py:331-332; test_workqueue.py:276, :414 and :419), each changing only to its criterion's expected outcome — the exit code, and the stderr where the criterion names it ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 5⟧
- [ ] every case the four scripts' existing suites hold passes ⟦full-suite⟧ ⟦criterion 5⟧

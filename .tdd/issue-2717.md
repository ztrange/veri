# Plan for #2717 — test_2380's kill of a leaf holding the suite lock does not depend on the leaf's start-up time, so a loaded full run cannot redden it

- [x] test_2380_a_leaf_that_hangs_after_acquiring_the_full_suite_lock_is_still_killed_stuck's hard timeout starts only once the leaf is known to hold the lock (or is otherwise independent of start-up time), still asserting (2, True) on a medium case with a real supervise.sh and a real leaf; only tests change, no production change ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] A medium case in test_supervise_process.py, with a real supervise.sh and a real leaf, whose leaf's start-up is delayed past 4 s before it reaches the lock still ends (2, True); no production change ⟦criterion 1⟧
- [x] A supervisor that no longer kills the hung leaf still reddens the case, watched going red and restored ⟦human-owed⟧ ⟦criterion 2⟧

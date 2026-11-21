# Plan for #4497 — revise.sh red crashes with a TypeError at attempt 2: the revise report carries no TEST_PATH

- [x] `revise.sh <n> red` at attempt 2, with `.tdd/develop-red.out` naming the step's `TEST_PATH` and `TARGET_TEST` and `.tdd/revise-red-1.out` holding no `TEST_PATH:` line, calls `restore-production.sh` with that test path and launches `revise-red-2` instead of exiting 2 with a TypeError (a small in-process case in `skills/tdd/scripts/tests/py/unit/test_revise.py`, failing on the current code) ⟦criterion 1⟧ ⟂ refactor pending

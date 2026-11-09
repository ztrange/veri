# Plan for #3284 — check-earlier reads a frozen test file moved by a suite-repair step as deleted, and nothing re-records the move

- [x] check-earlier refuses an earlier step's frozen case when its test file is deleted and the case has no counterpart at any path, naming the case (pins the deleted-file refusal before move-following code exists) ⟦criterion 3⟧
- [x] check-earlier refuses an earlier step's frozen case whose test file was moved (git mv) to a new path when the case's assertion changed in the move ⟦criterion 2⟧
- [x] check-earlier passes an earlier step's frozen case whose test file was moved (git mv, e.g. tests/py/test_x.py to tests/py/unit/test_x.py) with the case body identical, matching the case at its new path ⟦criterion 1⟧
- [x] check-earlier passes an earlier step's frozen case whose test file was moved when the only difference is a root-lookup line such as `parents[4]` changed to `parents[5]`, matching the case at its new path ⟦criterion 1⟧

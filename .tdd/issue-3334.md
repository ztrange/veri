# Plan for #3334 — affected-suites has no rule for projects/dashboard/, so it widens to veri's suites whose small-case guard refuses the dashboard's cases

- [x] `affected-suites.sh` for a range changing only `projects/dashboard/serve.py` prints the dashboard's own tests (`projects/dashboard/tests/...`) and no veri suite, with no "widening" message, pinned by a case ⟦criterion 1⟧
- [x] `affected-suites.sh` for a range changing a `projects/dashboard/` file and a veri file prints the union (the veri file's suites plus the dashboard's tests), pinned by a case ⟦criterion 2⟧
- [x] fix the full-suite failure: skills/tdd/scripts/tests/py/test_prd_014_1_removals.py — FAILED skills/tdd/scripts/tests/py/test_prd_014_1_removals.py::test_no_tracked_file_outside_the_record_names_the_removed_scripts - assert (0 == 1) (its git grep for the removed page name finds the new rule in skills/tdd/scripts/veri/affected_suites.py) ⟦suite-repair⟧ ⟦criterion 2⟧
- [ ] The new dashboard rule's guard, broken on purpose (the rule removed), is watched going red and restored ⟦human-owed⟧ ⟦criterion 3⟧

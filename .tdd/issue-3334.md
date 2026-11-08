# Plan for #3334 — affected-suites has no rule for projects/dashboard/, so it widens to veri's suites whose small-case guard refuses the dashboard's cases

- [ ] `affected-suites.sh` for a range changing only `projects/dashboard/serve.py` prints the dashboard's own tests (`projects/dashboard/tests/...`) and no veri suite, with no "widening" message, pinned by a case ⟦criterion 1⟧
- [ ] `affected-suites.sh` for a range changing a `projects/dashboard/` file and a veri file prints the union (the veri file's suites plus the dashboard's tests), pinned by a case ⟦criterion 2⟧
- [ ] The new dashboard rule's guard, broken on purpose (the rule removed), is watched going red and restored ⟦human-owed⟧ ⟦criterion 3⟧

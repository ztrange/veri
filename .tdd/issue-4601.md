# Plan for #4601 — A case a refactor moved byte-identical out of a still-existing frozen test file is found at its new path by tests-frozen check-earlier and rerecord-refactored

- [ ] `tests-frozen.sh check-earlier` exits 0 for a frozen Go case (body and helpers digests recorded in `a_test.go`) that was moved unchanged, with its helper, to a sibling `b_test.go` while `a_test.go` still exists without it ⟦criterion 1⟧
- [ ] `tests-frozen.sh rerecord-refactored` re-records such a byte-identical moved case at the sibling's path `b_test.go` (its body and helpers records name `b_test.go`) and exits 0, printing no `skipped:` line, when the recorded `a_test.go` still exists ⟦criterion 1⟧
- [ ] Guard: `tests-frozen.sh check-earlier` still exits 1 naming the case when a frozen case is missing from its still-existing recorded file and from every other file ⟦criterion 2⟧
- [ ] Guard: `tests-frozen.sh check-earlier` still exits 1 naming the case when a frozen case moved out of its still-existing recorded file into a sibling file with its body changed ⟦criterion 2⟧
- [ ] `tests-frozen.sh check-earlier` reads a moved case's helpers digest from the sibling file that now holds the case: it exits 1 naming the case when the helper in the holding file changed, even though the recorded file still holds the original helper unchanged ⟦criterion 3⟧

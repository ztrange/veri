# Plan for #4500 — revise.sh exits 2 building its prompt unless VERI_ISSUE is exported

- [x] `revise.sh <n> <phase>` run with no `VERI_ISSUE` in its environment builds the revise prompt with `VERI_ISSUE=<n>` and `VERI_STEP` set, as its leaf launch does, and launches the revise leaf ⟦criterion 1⟧

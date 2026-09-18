# Plan for #262 — refactor-touched.sh exits 1 for a bad commit and for a .tdd-only commit (pipefail takes grep's status)

- [x] refactor-touched.sh exits 2 with a stderr diagnostic naming the commit when the commit cannot be resolved ⟦criterion 1⟧
- [x] refactor-touched.sh exits 3 and prints nothing on stdout when the commit touches only .tdd/ ⟦criterion 2⟧

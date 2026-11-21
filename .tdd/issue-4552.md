# Plan for #4552 — verify-rebase judges a dirty tree: a rebase leaf's uncommitted fix passes verification and would be left out of the push

- [x] with a tracked file modified and uncommitted, `verify.sh rebase` exits 2 naming the dirty path and launches no verifier leaf ⟦criterion 1⟧

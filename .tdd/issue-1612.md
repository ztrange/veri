# Plan for #1612 — mutation-parity.sh treats an old suite that dies unmutated as passing; the revert-on-exception path is unpinned

- [ ] mutation-parity.sh reports a row `unproven` when its old suite dies before its count line run unmutated, with stderr naming the suite and saying it did not run to completion (a row whose unmutated old suite dies never reads `proven`) ⟦criterion 1⟧
- [ ] mutation-parity.sh reverts the row's mutation before an exception raised while the mutation is applied propagates, leaving the tree byte-identical to its state before the row; pinned by a case that raises with the mutation applied, checks the tree afterwards, and goes red when the revert-on-exception `finally` in veri/mutation_parity.py is removed ⟦criterion 2⟧

### `reorder-ledger-steps.sh` exits 1, leaving the ledger byte-identical and naming the step on stderr, when the step to move or the anchor is ticked (`- [x]`) or carries `⟂ refactor pending` ⟦criterion 2⟧
- the two ticked-step checks (`- [x]` on the moved step, then on the anchor) could share one helper, but the two error messages differ, so it saves little
- the anchor lookup runs again after `lines.pop(moved)` because the pop shifts indices. This could be derived from the first lookup, but the second lookup is simpler

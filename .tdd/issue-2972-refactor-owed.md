### `pin-recheck.sh <base-sha>` exiting 1 or 2 leaves no `.tdd/pin-recheck-ok`: a receipt an earlier run left is removed at the start of every run, before any record is read ⟦criterion 1⟧
- test-only | the two #2972 process tests each define the same local `git(*words)` helper; lift it into one shared helper

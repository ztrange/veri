# Plan for #1224 — add-ledger-step.sh tags an added step with its anchor's criterion, even when the step serves another

- [x] add-ledger-step.sh given `--criterion <k>` tags every inserted line with criterion k, whatever criterion the anchor step carries ⟦criterion 1⟧
- [ ] add-ledger-step.sh called without `--criterion` still tags inserted lines with the anchor's criterion, and an anchor with no criterion still yields untagged lines ⟦criterion 2⟧
- [ ] add-ledger-step.sh given `--criterion <k>` for a k no ledger step carries exits 2 with one stderr line naming k and leaves the ledger byte-identical ⟦criterion 3⟧

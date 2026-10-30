# Plan for #2713 — add-ledger-step.sh refuses a step text already carrying a criterion tag, so a ledger step never holds two

- [x] add-ledger-step.sh given a text already holding a criterion tag exits 2, names the tag on stderr and leaves the ledger byte-identical, with or without --criterion and for any position in a batch (one bad text inserts none); pinned by a case, run in-process through run_cli (small, no real process) ⟦criterion 1⟧
- [x] The guard, broken on purpose, goes red in that case ⟦human-owed⟧ ⟦criterion 2⟧

# Plan for #4671 — status.sh reports a finished run's unticked human-owed check as its current step

- [x] `status.sh` on a ledger whose only open record is a `⟦human-owed⟧` check, listed before a ticked step and none pending refactor, reports `step <m> of <m>`, not the check's number ⟦criterion 1⟧
- [x] `status.sh` on a ledger with an open `⟦human-owed⟧` check listed before an open ordinary step reports the ordinary step's number ⟦criterion 2⟧

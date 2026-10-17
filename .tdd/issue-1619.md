# Plan for #1619 — A corrupt events.jsonl makes add-ledger-step.sh bail suite-red (exit 1) instead of exit 2

- [ ] When .tdd/events.jsonl holds a line that is not valid JSON and the ledger already has a ⟦suite-repair⟧ step, add-ledger-step.sh inserting another ⟦suite-repair⟧ step exits 2 (never 1), its stderr names the log's path and the line it could not read, and the ledger is left byte-identical — pinned by a case with a malformed line ⟦criterion 1⟧

# Plan for #2952 — A step is ticked with no mutation record and nothing notices

- [x] tick-ledger.sh on an open step whose text names its go-red control as a file at a hex commit (the wording "the go-red control is", a path, "at", a 7-40 hex sha), with no .tdd/issue-<n>-mutations.md beside the ledger, exits 2, names the missing mutation record on stderr and leaves the ledger file byte-for-byte unchanged ⟦criterion 1⟧
- [x] tick-ledger.sh on an open step whose text holds the wording "mutation-probe.sh --before" followed by a 7-40 hex sha, with no mutation record file beside the ledger, exits 2, names the missing record on stderr and leaves the ledger unchanged ⟦criterion 1⟧ ⟂ refactor pending
- [ ] tick-ledger.sh on a step naming a before-sha control exits 0 and ticks the step once the mutation record file beside the ledger holds a before record for that same sha ⟦criterion 2⟧
- [ ] tick-ledger.sh on a step naming a before-sha control still exits 2 with the ledger unchanged when the mutation record file holds only a before record for a different sha ⟦criterion 1⟧
- [ ] tick-ledger.sh on a step naming its go-red control as a file at a hex commit exits 0 and ticks the step once the mutation record file holds a file/old/new record for that file ⟦criterion 2⟧
- [ ] tick-ledger.sh on a step whose text mentions "go-red control" bare, with neither wording and no mutation record file, ticks the step and exits 0 as before ⟦criterion 3⟧
- [ ] The guard, broken on purpose (the mutation-record existence check removed), turns the first criterion's case red, then is restored ⟦human-owed⟧ ⟦criterion 4⟧

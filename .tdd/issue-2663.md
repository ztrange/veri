# Plan for #2663 — A step's guard-subject test file stays editable after verify-red records it

- [x] `check --step` on a step carrying `⟦guard-subject: <path>⟧` still exits 1 naming a recorded test file that the marker does not name and whose content changed since the record (pin: already holds) ⟦criterion 1⟧
- [x] `check --step` exits 1 naming a recorded guard-subject file (the file the step's `⟦guard-subject: <path>⟧` marker names, captured by the record) that was deleted since the record, as an unrecorded deleted guard subject does (pin: already holds) ⟦criterion 2⟧
- [x] `check --step` exempts a recorded guard-subject file whose content changed since the record: with the file the step's `⟦guard-subject: <path>⟧` marker names captured by the record and then edited, it exits 0 and prints nothing ⟦criterion 1⟧

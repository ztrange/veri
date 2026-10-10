# Plan for #1436 — mutation-parity.sh reads every bash case whose FAIL line carries diagnostics as owed

- [x] A pairs-table row whose old bash case fails under its mutation with a FAIL line of the form `<old name> (<diagnostic>)` reads `proven` when the kept case catches the mutation, not `owed` ⟦criterion 1⟧
- [ ] A kept bash case whose FAIL line under the mutation is `<kept name> (<diagnostic>)` counts as catching the mutation, so the row reads `proven` rather than `unproven` ⟦criterion 1⟧
- [ ] A FAIL line that merely starts with the old case's name but continues with anything other than end of line or ` (` — another case whose name extends it — does not count as the old case failing, so the row reads `owed` ⟦criterion 1⟧

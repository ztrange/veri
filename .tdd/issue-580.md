# Plan for #580 — add-ledger-step.sh starts a new '## Owed steps' heading on every refusal instead of appending under the trailing one

- [x] A second refusal by add-ledger-step.sh appends its bullets under the existing trailing `## Owed steps` heading, so the ledger holds exactly one such heading carrying the first refusal's bullets followed by the second's ⟦criterion 1⟧
- [ ] A first refusal on a ledger with no `## Owed steps` heading still creates that heading with its bullets under it, and exits 1 ⟦criterion 2⟧
- [ ] A second refusal that appends under the existing heading still exits 1 and leaves the plan's checkbox steps byte-identical ⟦criterion 3⟧

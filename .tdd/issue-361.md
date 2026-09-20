# Plan for #361 — Refactor FLAGS: becomes NEW_STEP: and lands in the ledger

- [x] The prompt `build-develop-prompt.sh refactor …` builds ends its report with `NEW_STEP:` lines (or `NEW_STEP: none`) and carries no `FLAGS:` line ⟦criterion 1⟧
- [ ] SKILL.md's Refactor section passes the leaf's `NEW_STEP:` values to one `add-ledger-step.sh … after '<STEP>'` call after verify-refactor's final PASS, and commits the ledger with the refactor-pending clear ⟦criterion 2⟧
- [ ] SKILL.md's Refactor section marks each such insertion with a `step-added` event beside the `add-ledger-step.sh` call it made
- [ ] SKILL.md's Refactor section narrates `add-ledger-step.sh` exit 1 as owed steps and does not bail on it ⟦criterion 3⟧
- [ ] `refactor-triage.sh` exits with the same code for a report with `NEW_STEP:` lines as for the same report without them ⟦criterion 4⟧

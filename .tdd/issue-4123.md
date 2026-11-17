# Plan for #4123

- [ ] add-ledger-step.sh refuses a second ⟦lint-repair⟧ insertion in one run, ledger unchanged ⟦criterion 1⟧
- [ ] a ⟦lint-repair⟧ step carries ⟦added⟧ and is parked under ## Owed steps once growth is spent ⟦criterion 2⟧
- [ ] build-verify-prompt.sh diff renders the declared lint command for a ⟦lint-repair⟧ step only ⟦criterion 3⟧
- [ ] build-verify-prompt.sh diff keeps its arguments, options, environment and usage line ⟦criterion 4⟧
- [ ] verify-diff.md tells the verifier to run the lint command and REJECT on non-zero ⟦criterion 5⟧
- [ ] DRAFT-PR.md appends the lint repair step and handles its refusals ⟦criterion 6⟧
- [ ] DIFF-CHECKED.md says a ⟦lint-repair⟧ step's verifier runs the lint command ⟦criterion 7⟧

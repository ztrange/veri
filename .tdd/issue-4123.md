# Plan for #4123

- [x] add-ledger-step.sh refuses a second ⟦lint-repair⟧ insertion in one run, ledger unchanged ⟦criterion 1⟧
- [x] a ⟦lint-repair⟧ step carries ⟦added⟧ and is parked under ## Owed steps once growth is spent ⟦criterion 2⟧
- [x] build-verify-prompt.sh diff renders the declared lint command for a ⟦lint-repair⟧ step only ⟦criterion 3⟧
- [x] build-verify-prompt.sh diff keeps its arguments, options, environment and usage line ⟦criterion 4⟧
- [x] verify-diff.md tells the verifier to run the lint command and REJECT on non-zero ⟦criterion 5⟧
- [x] DRAFT-PR.md appends the lint repair step and handles its refusals ⟦criterion 6⟧
- [x] DIFF-CHECKED.md says a ⟦lint-repair⟧ step's verifier runs the lint command ⟦criterion 7⟧

# Plan for #675 — lib/ledger.sh's ledger_steps sets added=1 for any step quoting ⟦added⟧

- [x] ledger_steps reports added=0 for a step whose text quotes ⟦added⟧ mid-text and does not end in it ⟦criterion 2⟧
- [x] ledger_steps reports added=1 for a step whose text ends in ⟦added⟧ once a trailing ⟦criterion k⟧ and a trailing ⟂ refactor pending are stripped, done or open ⟦criterion 1⟧
- [ ] add-ledger-step.sh's is_added_step and ledger_steps' added column agree on every step line of add-ledger-step.test.sh's ledger fixtures ⟦criterion 3⟧

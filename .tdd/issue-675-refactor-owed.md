### ledger_steps reports added=0 for a step whose text quotes ⟦added⟧ mid-text and does not end in it ⟦criterion 2⟧
- extract the "ends in ⟦added⟧ once a trailing ⟦criterion k⟧ and ⟂ refactor pending are cut" check into one predicate in lib/ledger.sh, used by both ledger_steps and add-ledger-step.sh's is_added_step — needs steps 2 and 3 first, which make the two rules agree (pending-mark stripping, leading space)
### ledger_steps reports added=1 for a step whose text ends in ⟦added⟧ once a trailing ⟦criterion k⟧ and a trailing ⟂ refactor pending are stripped, done or open ⟦criterion 1⟧
- have add-ledger-step.sh's `added='⟦added⟧'` use lib/ledger.sh's `_ledger_added_mark` instead of a second copy
- have ledger_steps and is_added_step share one "ends in ⟦added⟧" check (they differ on the space before the mark, so this changes behaviour — plan step 3)

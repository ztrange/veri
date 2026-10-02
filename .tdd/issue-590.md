# Plan for #590 — add-ledger-step.sh counts a full-suite repair step against VERI_STEP_GROWTH, so the repair SKILL.md prescribes is refused and the run bails

- [x] add-ledger-step.sh inserts a text carrying ⟦suite-repair⟧ without an ⟦added⟧ mark and exits 0 with no ## Owed steps section, even when the ledger's ⟦added⟧ count already equals VERI_STEP_GROWTH, VERI_STEP_GROWTH=0 included ⟦criterion 1⟧
- [x] a ⟦suite-repair⟧ line already in the ledger does not count toward VERI_STEP_GROWTH: with the ⟦added⟧ count one below the budget, a further ordinary step is still accepted ⟦criterion 2⟧
- [x] a step carrying neither repair mark, at the budget, is still refused with exit 1 and filed under ## Owed steps, while a ⟦ci-repair⟧ step at the budget is still inserted without ⟦added⟧ ⟦criterion 3⟧
- [ ] next-unchecked.sh hands over an unchecked ⟦suite-repair⟧ step like any other step, never skipping it the way it skips a ⟦full-suite⟧ line ⟦criterion 4⟧
- [ ] SKILL.md's red-full-run paragraph gives the add-ledger-step.sh command appending a repair step carrying ⟦suite-repair⟧ that names the failing suite and its FAIL - line, and the git commit of the ledger ⟦criterion 5⟧
- [ ] SKILL.md's second-red-full-run bail is keyed on a ⟦suite-repair⟧ line already in the ledger, and still names every suite still red ⟦criterion 6⟧
- [ ] SKILL.md's ci-red bail still greps for ⟦ci-repair⟧ only, and states that a ledger holding a ⟦suite-repair⟧ step and no ⟦ci-repair⟧ step still gets its one CI repair attempt ⟦criterion 7⟧

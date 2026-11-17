# Plan for #4194 — /vplan shows each recommendation before and after the judge, and the human still decides

- [ ] ⟦skill-edit⟧ `operator/PRINCIPLES.md` P22 names `/vplan` as its one exception, the judge reviewing the planner's recommendation ⟦criterion 1⟧
- [ ] ⟦skill-edit⟧ `skills/vplan/SKILL.md` *2. Settle the decisions* passes each recommendation through `vjudge` and still asks every decision ⟦criterion 2⟧
- [ ] ⟦skill-edit⟧ `skills/vplan/SKILL.md` *2. Settle the decisions* shows the planner's and then the judge's recommendation, labelled ⟦criterion 3⟧
- [ ] ⟦skill-edit⟧ `skills/vjudge/SKILL.md` *Reviewing a recommendation* returns a verdict and records nothing ⟦criterion 4⟧
- [ ] `operator/GRADED`, `skills/vplan/GRADED` and `skills/vjudge/GRADED` hold a PASS line for the changed units ⟦criterion 5⟧

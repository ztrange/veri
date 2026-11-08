# Plan for #3353 — A planned step that deletes a mutation record has it restored, because no planner prose or requirement names the marker

- [x] skills/tdd/SKILL.md section 2 (Scope & plan) tells a planner that a step which deletes a committed mutation record names that record in its step text with the mutation-record directive, outside backticks and quotes (requirement PL67; change: add that planning sentence to section 2) ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] skills/tdd/SCRIPTS.md's supervise.sh entry states that a record a develop or revise leaf changed is restored with one mutation-record-restored event per record unless the step text names it as a directive, and that a quoted marker exempts nothing (requirement SC102) ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] The branch's SKILL.md and SCRIPTS.md prose changes each landed in a skill-edit commit of one unit, carrying that unit's requirement rows (PL67 with SKILL.md, SC102 with SCRIPTS.md) ⟦diff-checked⟧ ⟦criterion 3⟧

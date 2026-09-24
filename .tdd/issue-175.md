# Plan for #175 — A refactor flag becomes a plan amendment only when it names spec behaviour no step covers

- [x] The built refactor prompt reports overfit code on a FLAGS line carrying the class overfit, uncovered-spec or beyond-spec, or none, in place of the NEW_STEP line that carried it, and defines what each class names ⟦added⟧ ⟦criterion 1⟧
- [x] The refactor loop in SKILL.md answers an overfit flag with one triangulating red and green pair inside the current step, adding no ledger step and no second step-done, then resumes that step's refactor loop with the budget it had left ⟦criterion 2⟧ ⟂ refactor pending
- [ ] SKILL.md amends the plan from an uncovered-spec flag and from no other flag class ⟦criterion 3⟧
- [ ] SKILL.md narrates a beyond-spec flag as a follow-up in the Refactor comment and in the PR body, without planning or building it in this run ⟦criterion 3⟧
- [ ] SKILL.md runs a step's triangulation at most once, narrating a flag raised inside that triangulation's own refactor loop about the same code instead of triangulating it again ⟦criterion 4⟧

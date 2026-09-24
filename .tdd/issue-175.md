# Plan for #175 — A refactor flag becomes a plan amendment only when it names spec behaviour no step covers

- [ ] The built refactor prompt defines the overfit, uncovered-spec and beyond-spec flag classes and requires every flag line to carry one of them or to say none ⟦criterion 1⟧
- [ ] The refactor loop in SKILL.md answers an overfit flag with one triangulating red and green pair inside the current step, adding no ledger step and no second step-done, then resumes that step's refactor loop with the budget it had left ⟦criterion 2⟧
- [ ] SKILL.md amends the plan from an uncovered-spec flag and from no other flag class ⟦criterion 3⟧
- [ ] SKILL.md narrates a beyond-spec flag as a follow-up in the Refactor comment and in the PR body, without planning or building it in this run ⟦criterion 3⟧
- [ ] SKILL.md runs a step's triangulation at most once, narrating a flag raised inside that triangulation's own refactor loop about the same code instead of triangulating it again ⟦criterion 4⟧

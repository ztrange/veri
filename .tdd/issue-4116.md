# Plan for #4116 — PRD 032.2: the plan verifier rejects a predicate step with no counter-case beside it

- [ ] `prompts/verify-plan.md` rejects a plan whose predicate step's next Red/Green step is not its counter-case, naming the step and its condition, except when an earlier step is the counter-case or a committed case pins it, and only Red/Green steps count ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] `SKILL.md` *2. Scope & plan → the ledger* states the predicate/counter-case rule for the planner and PL19's and PL60's rules in one paragraph ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] `skills/tdd/SKILL.md` is no larger than at the base and the 3174 size case passes ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] `build-verify-prompt.sh plan` takes the same arguments, options and environment, its usage line unchanged ⟦diff-checked⟧ ⟦criterion 4⟧

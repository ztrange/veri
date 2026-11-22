# Plan for #4579 — verify-plan rejects a plan that leaves sites of the issue's goal outside the files a criterion's check reads

- [x] `skills/tdd/scripts/prompts/verify-plan.md` gains the goal-scope REJECT paragraph its three new `## Requirements` rows state, graded by `grade-prose.sh` ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] no line the branch adds to `skills/tdd/scripts/prompts/verify-plan.md` holds `{{`, and the branch changes no file under `skills/tdd/scripts/veri/` ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] `make test` passes ⟦full-suite⟧ ⟦criterion 3⟧

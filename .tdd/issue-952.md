# Plan for #952 — The PR body's "Refactor owed" section still lists transforms the end-of-run structural pass applied

- [x] `refactor-owed.sh applied <file> '<candidate>' <sha>` records that the structural pass applied a candidate, after which `refactor-owed.sh render <file>` no longer lists that candidate as owed under any step and instead lists it as applied, naming <sha> ⟦criterion 1⟧
- [x] `refactor-owed.sh render <file>` still lists as owed, as today, a structural candidate no `applied` call named, in the same file as one that was recorded applied ⟦criterion 2⟧
- [ ] SKILL.md's Draft PR structural pass runs `refactor-owed.sh applied` on the run's owed file with the candidate and the commit after each `transform` verifier PASS, before the PR body is rendered ⟦criterion 1⟧

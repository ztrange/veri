# Plan for #359 — refactor-owed.sh carries every step's structural leftovers into the draft PR

- [x] refactor-owed.sh append writes only the structural CANDIDATES lines of a report to the file, under the named step ⟦criterion 1⟧
- [x] two append calls for different steps leave both steps' candidates in the file ⟦criterion 2⟧
- [x] refactor-owed.sh render prints a "## Refactor owed" section listing every recorded candidate under its step ⟦criterion 3⟧ ⟂ refactor pending
- [ ] refactor-owed.sh render on an absent file, or one holding no candidate, exits 3 and prints nothing ⟦criterion 4⟧
- [ ] SKILL.md's Refactor section runs append for each step and commits the file with that step's refactor-pending clear ⟦criterion 5⟧
- [ ] SKILL.md's Draft PR section includes the render output in the PR body and omits it on exit 3 ⟦criterion 6⟧

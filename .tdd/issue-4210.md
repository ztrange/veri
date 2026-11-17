# Plan for #4210 — PRD 024.7b: the rows about Refactor loop are graded on that section

- [ ] `skill-edit-step.sh` and `skill-edit-guard.sh` take a `<file>#<heading>` unit: rows applied under its heading in the list beside its file, its file guarded, staged and committed, no file of its name created
- [ ] every row about *Refactor loop* moves to its `skills/tdd/SKILL.md#<heading>` unit, in order, split where it spans another section ⟦criterion 1⟧
- [ ] every tree audit naming a moved or retired row names its new unit ⟦criterion 6⟧
- [ ] the changed heading units and the whole-file unit are graded PASS once at the lane's final tip; `prose-owed.sh` prints nothing ⟦criterion 4⟧

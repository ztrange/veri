# Plan for #256 — run-conductor.test.sh case 4 compares the committed-skill prompt against the working-tree SKILL.md, so any step editing SKILL.md cannot go green

- [x] run-conductor.test.sh case 4 passes with an uncommitted edit to skills/tdd/SKILL.md in the tree under test, comparing against the committed SKILL.md ⟦criterion 1⟧
- [ ] case 4 still fails when what reaches the binary differs from the committed SKILL.md ⟦criterion 2⟧

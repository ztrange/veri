# Plan for #4789 — PRD 045.4: drop --refactor-owed

- [x] `skills/vgroom/SKILL.md` `## Invocation`, `## The sweep`, `## Applying outcomes` and `## Refactor-owed items` (renamed from `## --refactor-owed`) state the groom without the flag, rows GR1, GR3, GR5, GR9, GR13, GR18, GR19 and GR20 reworded to the issue's text, graded ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] `CLAUDE.md`'s refactor-owed bullet under *Invariants worth not breaking* names the sweep, not `/vgroom --refactor-owed`, row CM80 reworded to the issue's text, graded, and `skills/tdd/scripts/prose-owed.sh .` exits 0 ⟦skill-edit⟧ ⟦criterion 2⟧ ⟦criterion 4⟧
- [x] `docs/adr/0034-a-run-files-one-candidates-issue-for-what-it-leaves.md`'s `## Decision` grooming bullet says the issue is groomed by every `/vgroom` through its `## Refactor-owed items` section, naming PRD 045.4 as the change; `grep -rn -- '--refactor-owed' docs/adr/` prints nothing ⟦criterion 3⟧

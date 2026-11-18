# Plan for #4297 — /vgroom with no argument grooms every open issue; ids and ranges narrow it

- [x] `skills/vgroom/SKILL.md` says the no-argument sweep grooms every open issue (opted in or not, refactor-owed items through the consolidation, PRD trackers) save `taken:` ones, each reported as skipped with why, rows GR13 and GR14 reworded, graded ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] `skills/vgroom/SKILL.md` says an already opted-in issue is re-checked (gone, duplicate, stale rows, body format) and loses its opt-in label only with a reason in its report line, row GR15, graded ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] `skills/vgroom/SKILL.md` says a PRD tracker whose every planned slice is filed and closed, none waiting, is closed with that reason, and one with unfiled slices is reported with them, row GR16, graded ⟦skill-edit⟧ ⟦criterion 3⟧
- [ ] `skills/vgroom/SKILL.md` *Invocation* reads `/vgroom [<issue>...|<range>...|--refactor-owed]`, ids, ranges and `--refactor-owed` narrowing the sweep, row GR1 reworded, graded ⟦skill-edit⟧ ⟦criterion 5⟧
- [ ] `skills/vgroom/SKILL.md` *Invocation* accepts ids as `4261`, `#4261`, `4261 4262`, `4261,4262` and inclusive ranges `4260-4270`, `4260..4270`, skipped range numbers reported in one line, an explicit argument grooming exactly those issues, row GR17, graded ⟦skill-edit⟧ ⟦criterion 4⟧
- [ ] `skills/vgroom/SKILL.md` *Applying outcomes* files a consolidated refactor issue without asking unless it is big-impact, which is shown to the human first, row GR3 reworded, graded ⟦skill-edit⟧ ⟦criterion 6⟧

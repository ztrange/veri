# Plan for #4321 — PRD 034.5b: the dev session joins a reviewed run and lands a slice without being told

- [x] ⟦skill-edit⟧ `skills/vdev/SKILL.md` *Routing an exit* routes a reviewed ✅ Done run to `vmerge`'s join where `stack-branch.sh` exits 0, behind the outage hold (D142) ⟦criterion 1⟧
- [x] ⟦skill-edit⟧ `skills/vdev/SKILL.md` *Routing an exit* routes a join's exit 1 for a red stack to a retry after `stack-red.sh` exits 3, any other exit 1 to the human, an exit 2 reported never retried (D143) ⟦criterion 2⟧
- [x] ⟦skill-edit⟧ `skills/vdev/SKILL.md` runs `stack-land.sh` without `--now` after each join and each `stack-red.sh` exit 3, reporting by exit code (D144) ⟦criterion 3⟧
- [x] ⟦skill-edit⟧ `skills/vdev/SKILL.md` scopes the standing merge permission to `stack-land.sh` and `--now` to the human's ask (D145) ⟦criterion 4⟧
- [ ] ⟦skill-edit⟧ `skills/vdev/SKILL.md` never rebases a live run's branch across a landing (D146) ⟦criterion 5⟧
- [ ] `skills/vdev/REQUIREMENTS.md` lists D142-D146 and `skills/vdev/GRADED` signs the unit, `prose-owed.sh` exits 0 ⟦criterion 6⟧
- [ ] no touched skill or script names a repository, issue, branch, label or person ⟦criterion 7⟧

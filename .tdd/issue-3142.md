# Plan for #3142 — A dispatched review, hand-fix or merge subagent never leaves the primary clone dirty

- [x] `skills/vdev/SKILL.md`: every brief it gives a review, hand-fix or merge subagent says mutations (edit a file, run the suite, restore it) run only in a scratch clone or the run's own worktree, never in the primary clone (D25) ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] `skills/vdev/SKILL.md`: the same briefs say every `cd` in a chained command makes the whole command fail when it fails (`&&` or `set -e`), and a `;` never follows a `cd` or a guard whose failure would change where the next command runs (D26) ⟦skill-edit⟧ ⟦criterion 2⟧
- [ ] `skills/vdev/SKILL.md`: the same briefs have the subagent check `git -C <primary clone> status --porcelain` is empty before it reports, reporting any output as dirt, and forbid concurrent background jobs that share a scratch file (D27) ⟦skill-edit⟧ ⟦criterion 3⟧

# Plan for #4156 — PRD 033.1c: a merge failed by a GitHub incident holds merges until it closes

- [x] `skills/voutage/SKILL.md` exists and `voutage` is not in `LINKED` ⟦criterion 2⟧
- [x] every `$S/…sh` path `skills/voutage/SKILL.md` names resolves to an existing script ⟦criterion 3⟧
- [x] `voutage`'s Obeys line names `operator/PRINCIPLES.md` by a path found in the repo
- [ ] `skills/voutage/SKILL.md` states the outage procedure (VO rows), with `REQUIREMENTS.md` and a signed `GRADED` line, and `prose-owed.sh` exits 0 ⟦criterion 1⟧ ⟦criterion 4⟧ ⟦criterion 5⟧
- [ ] `skills/vdev/SKILL.md` routes `merge-failed`, holds merges while `.tdd/github-outage` exists and picks the mode up on start, recovery and resume; regraded ⟦criterion 6⟧

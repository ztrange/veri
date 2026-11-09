# Plan for #3478 — dispatch.sh skips a solvable issue whose named files an open run PR is changing, on any machine

- [x] dispatch.sh does not launch a solvable issue whose body names a path an open run draft PR changes, and launches the next one with no overlap ⟦criterion 1⟧
- [x] an issue skipped for overlap is launched at a later pass once no open run draft PR changes its paths ⟦criterion 2⟧
- [x] each skip prints one line naming the issue, the path and the PR ⟦criterion 3⟧
- [ ] when every solvable issue overlaps, dispatch.sh launches nothing that pass and never reports queue-empty ⟦criterion 4⟧
- [ ] ⟦skill-edit⟧ skills/tdd/SCRIPTS.md: the dispatch.sh entry states the skip ⟦criterion 5⟧
- [ ] ⟦skill-edit⟧ skills/vdev/SKILL.md: Launching states the skip ⟦criterion 5⟧

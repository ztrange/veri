# Plan for #3478 — dispatch.sh skips a solvable issue whose named files an open run PR is changing, on any machine

- [x] dispatch.sh does not launch a solvable issue whose body names a path an open run draft PR changes, and launches the next one with no overlap ⟦criterion 1⟧
- [x] an issue skipped for overlap is launched at a later pass once no open run draft PR changes its paths ⟦criterion 2⟧
- [x] each skip prints one line naming the issue, the path and the PR ⟦criterion 3⟧
- [x] when every solvable issue overlaps, dispatch.sh launches nothing that pass and never reports queue-empty ⟦criterion 4⟧
- [x] ⟦skill-edit⟧ skills/tdd/SCRIPTS.md: the dispatch.sh entry states the skip ⟦criterion 5⟧
- [x] a failed gh pr diff, PR list or issue-body read makes dispatch.sh exit 2 naming the failure, never launch on it (a rate-limited read waits for the reset) ⟦added⟧ ⟦criterion 1⟧
- [x] a skip line is printed once per (issue, PR, path) for the life of the dispatch process, not on every pass ⟦added⟧ ⟦criterion 3⟧
- [x] while every solvable issue overlaps, PR diffs are cached per (PR, head sha), issue bodies per process, and the open-PR list re-read at most once per VERI_DISPATCH_OVERLAP_POLL seconds (default 60; a bad value refused) ⟦added⟧ ⟦criterion 4⟧
- [x] the backtick-path extraction and the run-PR filter (draft on a tdd/ branch) are each pinned by a case that goes red when broken ⟦added⟧ ⟦criterion 1⟧
- [ ] ⟦skill-edit⟧ skills/vdev/SKILL.md: Launching states the skip ⟦criterion 5⟧

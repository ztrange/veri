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
- [x] ⟦skill-edit⟧ `skills/tdd/SCRIPTS.md`: the dispatch.sh entry states the once-per skip line, VERI_DISPATCH_OVERLAP_POLL and exit 2 on a failed overlap read (PR #3494 review) ⟦added⟧ ⟦criterion 5⟧
- [x] while the last slot decision launched nothing because every solvable issue overlapped, the queue read runs at most once per VERI_DISPATCH_OVERLAP_POLL seconds, and conductor exits are still reported at the normal cadence ⟦added⟧ ⟦criterion 4⟧
- [ ] a rate-limited open-PR list or issue-body read waits for the reset like the queue read, instead of exiting 2 ⟦added⟧ ⟦criterion 1⟧
- [ ] a failed open-PR list read and a failed issue-body read each exit 2 naming the failure and launch nothing, each pinned by a case that goes red when the failure is swallowed ⟦added⟧ ⟦criterion 1⟧
- [x] ⟦skill-edit⟧ skills/vdev/SKILL.md: Launching states the skip ⟦criterion 5⟧

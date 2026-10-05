# Plan for #866 — a run that stops at preflight leaves its skill pin behind for the next launch

- [ ] a launch whose conductor exits with no registered `.tdd/wt/<n>` worktree and no local `tdd/<n>-*` branch leaves no `.tdd/issue-<n>-skill-commit`, whether the conductor exits 0 or non-zero ⟦criterion 1⟧
- [ ] after a launch that left no worktree and no branch, the next launch of the same issue, with VERI_NEW_SKILL unset, pins the default branch's tip at that moment rather than the earlier launch's commit ⟦criterion 2⟧
- [ ] a launch whose conductor exits with `.tdd/wt/<n>` registered as a git worktree keeps `.tdd/issue-<n>-skill-commit`, and the next launch runs the recorded commit ⟦criterion 3⟧
- [ ] a launch whose conductor exits with a local `tdd/<n>-*` branch and no worktree keeps `.tdd/issue-<n>-skill-commit`, and the next launch runs the recorded commit; a branch for a different issue whose number merely starts with `<n>` (e.g. `tdd/<n>6-x`) does not count ⟦criterion 3⟧
- [ ] an unregistered `.tdd/wt/<n>` directory holding only `.tdd/events.jsonl`, as `VERI_NEW_SKILL=1` leaves it, does not count as a run past preflight: with no registered worktree and no branch the record is removed when the conductor exits ⟦criterion 4⟧
- [ ] a recorded commit the clone cannot resolve still exits 2 before launching any conductor, and `VERI_NEW_SKILL=1` still re-pins the record to the fresh tip and writes its `skill-repin` event ⟦criterion 5⟧
- [ ] `SKILL.md`'s *The skill snapshot* says the record survives only a run that got past preflight, and that this is decided after the conductor exits by a registered `.tdd/wt/<n>` worktree or a local `tdd/<n>-*` branch, not by the conductor's exit code ⟦criterion 6⟧
- [ ] every case `run-conductor.test.sh` and `issue-worktree.test.sh` already held on the default branch is still present with its assertions unchanged by this branch's diff ⟦diff-checked⟧ ⟦criterion 7⟧
- [ ] the repository's full test command passes ⟦full-suite⟧ ⟦criterion 7⟧

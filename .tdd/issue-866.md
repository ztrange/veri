# Plan for #866 — a run that stops at preflight leaves its skill pin behind for the next launch

- [x] a launch whose conductor exits with `.tdd/wt/<n>` registered as a git worktree keeps `.tdd/issue-<n>-skill-commit`, and the next launch runs the recorded commit ⟦criterion 3⟧
- [x] a launch whose conductor exits with a local `tdd/<n>-*` branch and no worktree keeps `.tdd/issue-<n>-skill-commit`, and the next launch runs the recorded commit ⟦criterion 3⟧
- [x] a launch whose conductor exits with no registered `.tdd/wt/<n>` worktree and no local `tdd/<n>-*` branch leaves no `.tdd/issue-<n>-skill-commit`, whether the conductor exits 0 or non-zero; the existing `run-conductor.test.sh` cases whose later launch relies on the record surviving a stub conductor (the resume-snapshot, keeps-its-pin and unresolvable-commit cases) model a run past preflight by giving their caller repo a local `tdd/<n>-*` branch in fixture setup, with their assertions unchanged ⟦criterion 1⟧
- [x] a local branch for a different issue whose number merely starts with `<n>` (e.g. `tdd/<n>6-x`) does not count as a run past preflight: the record is removed ⟦criterion 3⟧
- [x] after a launch that left no worktree and no branch, the next launch of the same issue, with VERI_NEW_SKILL unset, pins the default branch's tip at that moment rather than the earlier launch's commit ⟦criterion 2⟧
- [ ] an unregistered `.tdd/wt/<n>` directory holding only `.tdd/events.jsonl`, as `VERI_NEW_SKILL=1` leaves it, does not count as a run past preflight: with no registered worktree and no branch the record is removed when the conductor exits ⟦criterion 4⟧
- [ ] a recorded commit the clone cannot resolve still exits 2 before launching any conductor ⟦criterion 5⟧
- [ ] `VERI_NEW_SKILL=1` still re-pins the record to the fresh tip and writes its `skill-repin` event ⟦criterion 5⟧
- [ ] `SKILL.md`'s *The skill snapshot* says the record survives only a run that got past preflight, and that this is decided after the conductor exits by a registered `.tdd/wt/<n>` worktree or a local `tdd/<n>-*` branch, not by the conductor's exit code ⟦criterion 6⟧
- [ ] every case `run-conductor.test.sh` and `issue-worktree.test.sh` already held on the default branch is still present with its assertions unchanged by this branch's diff (fixture setup may change) ⟦diff-checked⟧ ⟦criterion 7⟧
- [ ] the repository's full test command passes ⟦full-suite⟧ ⟦criterion 7⟧

# Plan for #4388 — PRD 038.5: stop-settle.sh settles a stop (STOPPING.md 1-6) in one call

- [x] `stop-settle.sh <n> <mode>` (a `/bin/sh` shim over `veri/stop_settle.py`) refuses bad arguments and a missing `.tdd/issue-<n>-preflight` with exit 2 before any call ⟦criterion 7⟧
- [x] on a clean tree it runs the rebase/merge check, `git reset --hard HEAD`, `push-branch.sh`, the `stop mode=<mode> at=<at>` mark, `comment.sh <n> stopped` and `stop-requested.sh --clear`, in that order, and exits 0 ⟦criterion 1⟧
- [x] it waits on each `.tdd/<name>.pid` whose process still runs `supervise.sh <name>` before the tree check, and on none other ⟦criterion 1⟧
- [x] it derives `at` from the committed ledger: `unplanned`, `planned`, `green`, `step-done` ⟦criterion 2⟧
- [x] an interrupted rebase or merge marks `at=unsettled`, says what a human must finish, and resets and pushes nothing ⟦criterion 2⟧
- [x] a non-empty `git status --porcelain` stops it with exit 1 on `stopped at 2 tree-check` before any reset; `--drop` resets and names what it dropped ⟦criterion 3⟧
- [x] with `.tdd/restart-pending` naming a live pid the comment is the restart variant, a dead pid the operator one; it relaunches nothing ⟦criterion 4⟧
- [x] a `push-branch.sh` exit 1 or 2 is carried as `push=rejected sha=<remote-sha>` into the comment and it exits 0 ⟦criterion 5⟧
- [x] it writes no `bail` event, calls no `classify-bail.sh`, writes no metrics file, makes no commit, and leaves `.tdd/conductor.pid` in place ⟦criterion 6⟧
- [ ] it prints one line per call with its exit code and never a leaf's or a suite's output file ⟦criterion 7⟧
- [ ] a leaf wait whose slice runs out exits 3 with the wait record `.tdd/issue-<n>-stop-settle-wait`; called again by the same conductor it only waits again ⟦criterion 7⟧
- [ ] `STOPPING.md` opens with the call line (SP24) and `SCRIPTS.md` lists the script (SC584), both graded; `SKILL.md` unchanged ⟦criterion 8⟧

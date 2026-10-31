# Plan for #2768 — watch-runs.sh reports a live conductor as vanished while its worktree is being cut

- [x] With the issue in the started list, `.tdd/wt/<n>/` absent and no `run_conductor.py <n>` process alive, `watch-runs.sh` prints `vanished <n>` and exits 2 ⟦criterion 2⟧
- [x] With the issue in the started list, `.tdd/wt/<n>/` absent for several consecutive polls and the issue's `run_conductor.py <n>` process alive, `watch-runs.sh` does not print `vanished` or exit 2 ⟦criterion 1⟧ ⟂ refactor pending

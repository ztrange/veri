# Plan for #2597 — status.sh --json and watch-runs.sh answer when no run exists, instead of watch-runs.sh crashing on non-JSON

- [x] `status.sh --json` with no run directory under `.tdd/wt/` prints a JSON document whose `runs` list is empty and exits 3 (plain `status.sh` keeps printing `no runs`); pinned by a small in-process case ⟦criterion 1⟧
- [x] `watch-runs.sh` with no run directory and no arguments prints `nothing to watch` and exits 3, never 2; pinned by a small in-process case ⟦criterion 2⟧
- [ ] `watch-runs.sh --max-wait <n>` with no run directory prints `timeout` and exits 3 once the bound passes, never 2; pinned by a small in-process case with the clock and wait injected (no real sleep) ⟦criterion 2⟧

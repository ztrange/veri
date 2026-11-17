# Plan for #4225 — PRD 035.4b: the metrics report each run of an issue

- [x] on a journal of two runs and a restart, `metrics.sh <n> --json` holds `runs`, one entry per run in order with `index`, `ended`, `cause`, `wall_seconds`, `awake_seconds`, `sessions`, `leaves` and `cost_usd` ⟦criterion 1⟧
- [x] the `runs` entries' `leaves` and `cost_usd` sum to the issue's leaf totals ⟦criterion 1⟧
- [x] a journal with no `done`, `bail` or `stop` line folds as one open run ⟦criterion 2⟧
- [x] `PUBLISHED.md` states `runs`, its keys and the boundary rule (PB18) ⟦criterion 3⟧

# Plan for #4006 — PRD 024.1: the metrics report says what the conductor did with each green REJECT

- [x] `metrics.layout` prints a `#### Green rejects` row per green-reject row of a hand-built `Fold` ⟦criterion 6⟧
- [ ] `metrics.sh <n>` prints one `#### Green rejects` row per green `verdict=REJECT` event, in log order; other phases and PASSes add none ⟦criterion 1⟧
- [ ] a row's route is the first later same-step `reroute` kind, `revise`, or `bail`, else `none`; other steps' events skipped ⟦criterion 2⟧
- [ ] a row's reason escapes each `|` with a backslash, and reads `unknown` when the event has no `reason` ⟦criterion 3⟧
- [ ] below the table, `Green rejects by route: <route> <count>, …` ordered by count descending, then route name ⟦criterion 4⟧
- [ ] a log with no green REJECT prints `Green rejects by route: none` and no table ⟦criterion 5⟧

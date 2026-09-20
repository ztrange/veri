# Plan for #342 — Test-command runs record a tier/seconds event; the conductor posts a soft warning over budget

- [x] a test-command run made through the new wrapper writes one `test-run` event carrying `tier`, `suites` and `seconds`, and exits with the command's own status ⟦criterion 1⟧
- [x] the "usual" for a tier is the median of that tier's last 10 `test-run` events' seconds, read out of `.tdd/events.jsonl` ⟦criterion 2⟧
- [x] `VERI_UNIT_BUDGET` and `VERI_TIME_WARN_RATIO` unset resolve to `10` and `1.5`, and a non-numeric value for either exits 2 with a diagnostic naming the variable ⟦criterion 3⟧
- [x] a unit-tier run whose seconds exceed `VERI_UNIT_BUDGET` is over budget; at or under it, it is not ⟦criterion 4⟧
- [ ] a run of any tier whose seconds exceed `VERI_TIME_WARN_RATIO` × its usual is over budget; at or under the ratio, it is not ⟦criterion 5⟧
- [ ] the over-budget answer prints exactly one `⏱` line for a run over budget and nothing for one that is not, and SKILL.md instructs the conductor to paste that line into the phase's narration and to branch on nothing ⟦criterion 7⟧
- [ ] an over-budget test run leaves a run's outcome alone: the verdict stands and nothing retries or bails because of the seconds ⟦criterion 6⟧
- [ ] `metrics.sh <issue>` prints a new per-tier section of the `test-run` events' recorded seconds, reading only `.tdd/events.jsonl` ⟦criterion 8⟧

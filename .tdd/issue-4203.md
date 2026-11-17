# Plan for #4203 — PRD 035.1: metrics.sh <n> --json prints the run's metrics as JSON

- [x] `metrics.sh <n> --json` prints exactly one JSON object and exits 0; `metrics.sh <n>` prints the markdown report unchanged ⟦criterion 1⟧
- [ ] the object is built by a function that takes a `Fold` and reads no event, ledger or log ⟦criterion 2⟧
- [ ] `phases` holds one entry per leaf phase, keyed by phase, equal to the markdown's By phase row ⟦criterion 3⟧
- [ ] `steps` holds one entry per step in the markdown's order, with `text`, the phase keys, `retries`, `no_verdict` and the step's start-to-done `wall_seconds` ⟦criterion 4⟧
- [ ] `conductor` holds `cost_usd`, `turns`, `sessions`, `model`, `estimated` and `priced` (true, false or "partial") ⟦criterion 5⟧
- [ ] `total` holds the markdown's total row and `includes_conductor` ⟦criterion 6⟧
- [ ] `run` holds `issue`, `outcome`, `wall_seconds`, `awake_seconds` (null before `done`) and every `bail` as `{cause, classification, phase, step}` ⟦criterion 7⟧
- [ ] every count, duration and cost is a number, and an unknown figure is `null` ⟦criterion 8⟧
- [ ] no key at any depth names a rate, a percentage or an average ⟦criterion 9⟧
- [ ] under `--json` a missing issue or an unreadable log is exit 2 with nothing on stdout, and any other argument after the issue is exit 2 with the usage line ⟦criterion 10⟧
- [ ] `SCRIPTS.md`'s `metrics.sh` entry states `--json` (SC264), graded ⟦criterion 11⟧

# Plan for #4223 — PRD 035.3b: the metrics count how often a developer phase passed first try

- [x] each `phases.<phase>` entry of `metrics.sh <n> --json` holds `verified_steps`, `first_try_pass` and `revise_cycles`: a step passed first try and a step passed after two revises ⟦criterion 1⟧
- [ ] a journal with no `revise` event folds with every `revise_cycles` `0` ⟦criterion 2⟧
- [ ] `PUBLISHED.md` states the three keys under the phase entry and what `revise_cycles` `0` means on an old journal (PB16) ⟦criterion 3⟧

# Plan for #4625 — metrics.sh counts Steps done from step-done events, not the ledger, so a finished run reports fewer steps done

- [ ] a run whose committed ledger has all N plan steps done, its events log missing an earlier session's `step-done` marks, reports `Steps done: N of N planned.` ⟦criterion 1⟧
- [ ] a ledger step ticked green but still `⟂ refactor pending` is not counted as done

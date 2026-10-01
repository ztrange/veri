# Plan for #604 — a leaf's usage event and the run's metrics record which model answered

- [x] the `usage` event harvest-usage.sh appends carries a `model` key naming the one model a result record's `modelUsage` lists ⟦criterion 1⟧
- [x] when `modelUsage` names more than one model, the usage event's `model` key lists every one of them ⟦criterion 1⟧
- [ ] when `modelUsage` names more than one model, the usage event keeps each model's own token and cost figures alongside, rather than only their sums ⟦criterion 1⟧
- [ ] a result record with no `modelUsage` still yields a `usage` event with `model` empty, and harvest-usage.sh's exit code and stderr for it are unchanged ⟦criterion 2⟧
- [ ] metrics.sh prints a "By model" table with one row per (role, model) — role developer or verifier — carrying the same columns as "By phase" ⟦criterion 3⟧
- [ ] the metrics report's header states the run's requested model knobs (`VERI_MODEL`, `VERI_MODEL_DEVELOPER`, `VERI_MODEL_VERIFIER`, each or "unset") next to the models that actually answered ⟦criterion 4⟧
- [ ] an event log whose `usage` events carry no `model` key still produces a metrics report, its "By model" table saying the model was not recorded ⟦criterion 5⟧

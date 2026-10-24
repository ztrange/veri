# Plan for #2265 — add-ledger-step writes its step-added event without ts or awake, breaking stop-reason.sh and the metrics awake clock

- [x] The step-added record add-ledger-step.sh appends to .tdd/events.jsonl carries an integer ts and an awake reading, written through veri/event.py as every other event is, and keeps event step-added, actor add-ledger-step and the inserted step text so ledger-growth.sh still matches it ⟦criterion 1⟧
- [x] On a run log whose step-added record was written by add-ledger-step.sh, stop-reason.sh exits without a KeyError and metrics.sh still reports the awake clock rather than saying the log carries no awake-clock reading ⟦criterion 2⟧

# Plan for #1045 — Refactor owed by #1031

- [x] `ledger_step_index` in skills/tdd/scripts/veri/preserve_attempt.py names the index and text fields of each `ledger_steps` record (unpacked or otherwise named) instead of reading them as `record[0]` and `record[6]`, with no other line of the branch's diff changing behaviour ⟦diff-checked⟧ ⟦criterion 1⟧

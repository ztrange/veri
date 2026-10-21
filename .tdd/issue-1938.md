# Plan for #1938 — stop-reason.sh judges a conductor log by its latest launch only

- [ ] For a conductor log holding two launches (each starting with a `{"type":"system","subtype":"init"}` record) where the last launch has no `result` record, `stop-reason.sh <n>` exits 2 with `no result record in <log>` and never prints the earlier launch's reason, pinned by a small in-process case ⟦criterion 1⟧
- [ ] For a conductor log holding two launches where the last launch has a `result` record, that record alone decides between `usage-limit` and `unknown`, whatever the earlier launch's result said, pinned by a small in-process case ⟦criterion 2⟧

# Plan for #4131 — a process case's stub processes have ended when the case ends

- [x] the report-refresh case's stub `report-cache.sh refresh` has ended when the case ends, also when it had not opened its fifo at the release ⟦criterion 1⟧
- [ ] the stub `claude` that `live_conductor` starts has ended when the `started` fixture tears down, also when its `claude.pid` was never read ⟦criterion 2⟧

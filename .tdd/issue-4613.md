# Plan for #4613 — run-step.sh follows a stale rejected/half record over the reroute's phase (revise green after route=revise phase=red; resume skips red)

- [x] `run-step.sh <n>` called again with `.tdd/issue-<n>-step` recorded at green-half before a reroute to red (red-half's rejected record naming the step) does not skip red: it calls `revise.sh <n> red` first, never starting at green-half ⟦criterion 2⟧
- [ ] `run-step.sh <n>` called after a reroute to red, with a stale green-half rejected record also naming the step, calls `revise.sh <n> red` and then green-half afresh, never `revise.sh <n> green` ⟦criterion 1⟧

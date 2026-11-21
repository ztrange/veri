# Plan for #4544 — refactor-half.sh passes the ledger's last commit, not the step's green tick, as verify-refactor's BASE_SHA after a re-pin

- [ ] with a re-pin tick after the step's green tick on the ledger, refactor-half.sh launches verdict-refactor with the step's green tick (fused_step.green_tick) as BASE_SHA, not the ledger's last commit ⟦criterion 1⟧

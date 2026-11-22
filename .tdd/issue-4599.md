# Plan for #4599 — metrics.sh counts each background-task wake of one conductor session as a session, summing its cumulative total_cost_usd (~8x overstated), and growth.py resets per wake so restart-conductor.sh never fires

- [ ] metrics: a conductor stream log whose result records repeat a session_id prices that session at its last total_cost_usd and counts it once, so wakes 2.00, 5.00 of one session and 1.00 of another give $6.00 in 2 sessions ⟦criterion 1⟧
- [ ] growth: an init record carrying the same session_id as the previous init keeps the session's first usage as the baseline; a new session_id still resets it (#3369) ⟦criterion 2⟧
- [ ] restart-conductor: with the default VERI_RESET_GROWTH_CONDUCTOR, a one-session conductor log whose first usage is 78446 and whose context rises in steps to 110000 gets an at-ledger stop request before the context passes 110000 (default lowered from 70000 to 30000) ⟦criterion 3⟧

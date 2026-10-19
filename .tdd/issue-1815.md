# Plan for #1815 — metrics.py prices a conductor turn's 1-hour cache writes at the 5-minute rate

- [x] A conductor turn whose usage carries both `cache_creation.ephemeral_1h_input_tokens` and `cache_creation.ephemeral_5m_input_tokens` is priced in metrics.py's per-turn cost with its 1-hour tokens at the 1-hour cache-write rate (opus 30.00 $/Mtok) and its 5-minute tokens at the 5-minute rate (18.75 $/Mtok), seen in the rendered per-turn dollars and the session total ⟦criterion 1⟧
- [ ] metrics.py's per-turn pricing reads session_cost.py's `PRICES` table: changing a rate in `veri.session_cost.PRICES` changes the per-turn dollars metrics renders, so the two tables cannot disagree ⟦criterion 2⟧
- [ ] The branch's diff adds a pytest case in which one conductor turn carries both 1-hour and 5-minute cache-creation tokens and asserts its price ⟦diff-checked⟧ ⟦criterion 3⟧

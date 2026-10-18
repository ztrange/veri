# Plan for #1707 — Leaves write their prompt cache at the 5-minute TTL, not the 1-hour one

- [ ] A leaf launched through run-leaf.sh requests the 5-minute cache TTL (FORCE_PROMPT_CACHING_5M=1 in the claude binary's environment), so a stub claude that writes its cache at 5 minutes when asked reports ephemeral_5m_input_tokens non-zero and ephemeral_1h_input_tokens zero in the leaf's stream usage ⟦criterion 1⟧
- [ ] The conductor launched through run-conductor.sh does not request the 5-minute cache TTL (no FORCE_PROMPT_CACHING_5M in the claude binary's environment), so a stub claude reports its cache writes as ephemeral_1h_input_tokens ⟦criterion 2⟧

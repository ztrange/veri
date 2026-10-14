# Plan for #1443 — A print-mode conductor ends its turn while its own subagent is still running, and the run exits with no Bail or Done

- [ ] SKILL.md says the conductor never ends its turn while anything it started is still running — a background command, a subagent, or a background task — and says how it waits for one inside the turn, covering the mutation-parity pairs table, which it builds inline or waits for inside the turn; a prose case goes red when that sentence is removed or its "never" is negated ⟦criterion 1⟧

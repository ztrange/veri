# Plan for #2652 — The dev session's merge caveats name GitHub's secondary rate limit: quota left means use REST, never wait for the reset

- [ ] skills/veri-dev/SKILL.md satisfies row D19: the *Caveats before any merge* bullet says a GitHub call refused with `rate limit exceeded` while `gh api rate_limit` still reports quota hit GitHub's secondary limit, and to use REST rather than wait for the reset; graded PASS ⟦skill-edit⟧ ⟦criterion 1⟧

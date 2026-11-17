# Plan for #4091 — PRD 016.6c: /vready proves leaves may bypass permission prompts

- [x] a `bypassPermissions` row runs `claude -p --model haiku --permission-mode bypassPermissions --output-format json` in a scratch directory under `.tdd/`, ok when both nonce files hold the nonce and no denial is listed, starting no process but `claude` ⟦criterion 1⟧ ⟦criterion 6⟧
- [x] an exit 0 with `is_error` false but a nonce file missing or not holding the nonce fails the row ⟦criterion 2⟧
- [x] a listed permission denial fails the row though both files hold the nonce ⟦criterion 2⟧
- [x] a failing row quotes the denied tools and names both managed-settings files and the user and project `permissions.deny` ⟦criterion 3⟧
- [x] the probe's `claude` is started with `strip_session_env` applied ⟦criterion 4⟧ ⟦criterion 6⟧
- [x] the scratch directory is gone on every exit with 0, 1 or 2, and nothing else is written ⟦criterion 5⟧
- [ ] a probe that never answers fails the row instead of hanging the check
- [ ] vready SKILL.md `## Run` says the check makes one paid Haiku call, about $0.004 ⟦criterion 7⟧
- [ ] README `## Install` says `/vready` makes that paid call and names its cost ⟦criterion 8⟧

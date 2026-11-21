# Plan for #4465 — PRD 041.2: delete the dev session's reset scripts, verb and tunables

- [x] `role-growth.sh`, `reset-wait.sh`, `veri/role_growth.py`, `veri/reset_wait.py` and their tests are gone, pinned by a case asserting none of those paths exists ⟦criterion 1⟧
- [x] `role-state.sh dev request-reset` exits 2 as an unknown verb, `set resetter <id>` exits 2 as an unknown field, and `recovered` still records the session id ⟦criterion 2⟧
- [x] `role-state.sh dev set` refuses each role-growth-only field (`session`, `transcript`, `baseline`, `baseline-at`, `refused-at`, `refused-now-at`) as unknown, and the usage line names none of them ⟦criterion 3⟧
- [ ] a role state file still holding a `resetter` line is read without error by `status.sh --recover dev` and by `dispatch.sh`, the line ignored ⟦criterion 4⟧
- [ ] `VERI_RESET_GROWTH_DEV`, `VERI_RESET_ACK_TIMEOUT` and `VERI_RESET_MAX_PER_HOUR` are gone from `veri/tunables.py` and `veri/README.md`'s tunables table, `VERI_RESET_GROWTH_CONDUCTOR` kept in both ⟦criterion 5⟧
- [ ] `reset-cost.sh dev …` exits 2 with the usage line, and `reset-cost.sh conductor <n>` prints what it prints today ⟦criterion 6⟧
- [ ] `skills/tdd/SCRIPTS.md` names no `role-growth.sh`, `reset-wait.sh`, `request-reset`, `resetter` or `dev` mode of `reset-cost.sh`, its rows SC134/SC137 dropped and SC135/SC220 rewritten, regraded ⟦criterion 7⟧
- [ ] `veri/README.md` lists no deleted script or module ⟦criterion 8⟧
- [ ] `make unreachable` lists no script this issue left behind ⟦criterion 9⟧

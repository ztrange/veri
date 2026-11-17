# Plan for #4103 — PRD 026.8: the role scripts take one role

- [ ] the four role scripts exit 2 on `coord`, writing nothing, usage naming `dev` alone ⟦criterion 1⟧
- [ ] `role-state.sh dev set|drop coordinator` exit 2; recovery's State lists no `coordinator` line ⟦criterion 2⟧
- [ ] `role_growth.py` reads no `VERI_RESET_GROWTH_COORD` ⟦criterion 3⟧
- [ ] `metrics.sh` adds no `Coordinator` row for a `/vcoord` transcript ⟦criterion 4⟧
- [ ] an existing `.tdd/role-coord*.state` survives each script given `coord` byte for byte ⟦criterion 5⟧
- [ ] SCRIPTS.md entries and shim usage comments name the dev session alone; skills/tdd regraded ⟦criterion 6⟧
- [ ] a guard case greps skills/tdd outside tests for vcoord/coordinator/VERI_RESET_GROWTH_COORD/coord ⟦criterion 7⟧
- [ ] the guard is watched red on a word put back and on `vcoord` in `LINKED` ⟦criterion 8⟧

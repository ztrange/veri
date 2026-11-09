# Plan for #3370 — dispatch.sh reports a conductor replaced by a planned restart as silent-exit

- [x] dispatch.py main: a run in seen, absent from live_conductors, whose worktree holds .tdd/restart-pending, prints no exit line (no silent-exit, done or bail) on that pass and dispatch keeps looping; pinned by one small case in skills/tdd/scripts/tests/py/unit/test_dispatch.py ⟦criterion 1⟧ ⟂ refactor pending
- [ ] Guard: a run absent from live with no restart in flight and no Done/Bailed comment still prints silent-exit <n>; ignore the restart marker on purpose, see the first case go red, restore ⟦human-owed⟧ ⟦criterion 2⟧

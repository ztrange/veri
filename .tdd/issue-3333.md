# Plan for #3333 — pin-recheck labels a red pytest run 'mutation did not build' when the base's one-line output shares no line with it

- [ ] A mutated run that fails with no pytest failure marker and no line shared with the base (a real build error) is still reported "mutation did not build" by pin_recheck, exit 1, pinned by a case in skills/tdd/scripts/tests/py/ driving pin_recheck in-process with faked base and mutated runs ⟦criterion 2⟧
- [ ] A pin whose command is a single-case pytest run, its base printing only `1 passed in 0.19s` and its mutated run failing with pytest's `FAILED` / `AssertionError` output, is judged red by pin_recheck (no "mutation did not build", exit 0), pinned by a case in skills/tdd/scripts/tests/py/ driving pin_recheck in-process with faked base and mutated runs ⟦criterion 1⟧
- [ ] The pytest-failure recognition's guard, broken on purpose (always false), goes red ⟦human-owed⟧ ⟦criterion 3⟧

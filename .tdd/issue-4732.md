# Plan for #4732 — A step that replaces a split step with identical text inherits the old step's spent revise attempts

- [ ] With two conductor `revise` marks for phase `green` on step S followed by a `step-split` event replacing S (its `anchor` S), `spent(wt, S, "green")` in `veri/revise.py` returns 0: revise marks recorded before the step-split that replaced the step do not count (a small in-process case in `skills/tdd/scripts/tests/py/unit/test_revise.py`) ⟦criterion 1⟧
- [ ] With two conductor `revise` marks for phase `green` on step S and no `step-split` event after them, `spent(wt, S, "green")` in `veri/revise.py` still returns 2 (a small in-process pin case in `skills/tdd/scripts/tests/py/unit/test_revise.py`) ⟦criterion 2⟧

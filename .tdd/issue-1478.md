# Plan for #1478 — Refactor owed by #1465

- [ ] Move Method: `leaf_role.py` gains the revise predicate `is_revise(name)` (true for `revise-*` names and `develop-exhausted`), and `leaf_model.py`'s `resolve` asks it instead of matching leaf names itself; no test file changes. Predicate: `grep -q '^def is_revise(' skills/tdd/scripts/veri/leaf_role.py && ! grep -qE 'startswith\("revise-"\)|develop-exhausted' skills/tdd/scripts/veri/leaf_model.py` ⟦criterion 2⟧
- [ ] Behaviour unchanged: every existing case keeps its name and outcome, every leaf name gets the same model as before — the full suite (`make test`) is green on the branch with no test file edited ⟦full-suite⟧ ⟦criterion 1⟧

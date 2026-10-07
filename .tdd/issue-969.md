# Plan for #969 — test_metrics.py's by-step kind case no longer pins 'not its leaf count': its pinned and satisfied steps launch no leaves

- [x] In the leaf-count case of tests/py/test_metrics.py, the many-pin and many-sat fixture steps each carry more launch events than two-leaf (at least the old bash fixture's four red-phase launches across two attempts plus the verdict-pin launch), and the case still asserts {"many-pin": "pin", "many-sat": "already-satisfied", "two-leaf": "full"} ⟦criterion 1⟧
- [ ] With the By-step kind computed from the step's leaf count in a scratch copy of veri/metrics.py, the strengthened case goes red; restored, it is green again (veri/__pycache__ cleared before trusting the result) ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] veri/metrics.py is unchanged on the branch ⟦diff-checked⟧ ⟦criterion 3⟧

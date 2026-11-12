# Plan for #3710 — Refactor: Single-source the skill-edit step test in ledger.py

- [x] Extract Function: the skill-edit unit/heading check in `skills/tdd/scripts/veri/scope_check.py` moves out of `main` into a named function that `main` calls (no production behaviour change; no test file edited); predicate, false before and true after: `awk '/^def main\(/{m=1;next} m&&/^[^ \t#]/{m=0} m' skills/tdd/scripts/veri/scope_check.py | grep -cE 'unit_of|requirements_lines'` prints 0 and `grep -cE '^def [a-z_]+\(' skills/tdd/scripts/veri/scope_check.py` prints 3 ⟦criterion 1⟧
- [ ] Both exit-2 messages of `scope_check.py` ("no path-shaped unit for skill-edit step: ..." and "no ### heading for skill-edit unit: ...") and their exit code 2 are unchanged by the branch's diff ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] Behaviour preserved: the existing suites stay green (`make test`) ⟦full-suite⟧ ⟦criterion 3⟧

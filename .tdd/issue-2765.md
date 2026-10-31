# Plan for #2765 — tests_frozen's case pattern truncates a JS title at an escaped quote and drops backtick titles

- [x] A JS test title holding an escaped quote of its own kind, double-quoted or single-quoted, is recorded by tests_frozen whole and with the escaping removed; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py, parametrized over the two quote kinds ⟦criterion 1⟧
- [x] Two JS test titles that differ only after an escaped quote are recorded by tests_frozen as two separate cases; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py ⟦criterion 2⟧
- [x] A JS test title in backticks with no dollar-brace interpolation is recorded by tests_frozen; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py ⟦criterion 3⟧ ⟂ refactor pending
- [ ] A JS test title in backticks holding a dollar-brace interpolation is recorded by tests_frozen, whole and as written in the source, never silently dropped; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py ⟦criterion 4⟧

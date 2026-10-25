# Plan for #2359 — A fixture-repair step may edit its named fixture file even when that file holds its recorded Red case

- [x] `tests-frozen.sh check --step` on a fixture-repair step whose recorded Red case lives in the named fixture file exits 1, naming that file, when Green changed the recorded case's own body (a pytest case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py; no production change expected — it pins today's refusal) ⟦criterion 1⟧
- [ ] `tests-frozen.sh check --step` on a fixture-repair step whose recorded Red case lives in the named fixture file exits 0 when Green changed that fixture file only outside the recorded case's body, while the recorded case itself stays frozen (a pytest case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py) ⟦criterion 1⟧

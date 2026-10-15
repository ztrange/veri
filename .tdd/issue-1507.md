# Plan for #1507 — verify-green returns PASS while its own REASON says the step's named bash cases were not deleted

- [x] On a ⟦replaces-case⟧ step, when the green verifier leaf answers VERDICT: PASS and a case the --step text names is still in its suite, verify.sh green exits 1 (REJECT) with a stdout reason naming each surviving case, whatever the leaf's REASON said; the survivors check runs after the leaf and adds no verifier parameter. Pinned in tests/py/test_verify.py by a stub PASS leaf on a step naming two cases, one still present in the scratch suite ⟦criterion 1⟧
- [ ] On a ⟦replaces-case⟧ step, when the green verifier leaf answers VERDICT: PASS and the named-cases check cannot answer (its exit 2, e.g. an unreadable suite), verify.sh green exits 2 ⟦criterion 1⟧
- [ ] A green verify on a step without ⟦replaces-case⟧ returns the leaf's verdict unchanged (a stub PASS leaf exits 0 even though no named-cases check applies) ⟦criterion 2⟧
- [ ] A green verify on a ⟦replaces-case⟧ step whose every named case is gone from its suite, with a stub PASS leaf, still exits 0 ⟦criterion 2⟧

# Plan for #2846 — parse-verdict keeps only the first line of a REASON printed before the verdict, so its bullets never reach the next brief

- [x] Output with a multi-line `REASON:` before `VERDICT: REJECT` and nothing after it exits 1 and prints every line of the reason, in order; free-form text before the `REASON:` line stays out of the printed reason (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 1⟧
- [ ] With `MISSING_TEST: <behaviour>` before a multi-line `REASON:` block and `VERDICT: REJECT` after it, the output holds the `MISSING_TEST:` line intact followed by the whole block (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 2⟧
- [ ] A `FLAGS:` line between a multi-line `REASON:` block and `VERDICT: REJECT` is not printed as part of the reason, while the block's other lines still are (a small in-process case in skills/tdd/scripts/tests/py/unit/test_parse_verdict.py) ⟦criterion 3⟧
- [ ] `preceding_reason`, broken on purpose to keep only the `REASON:` line, turns the first criterion's case red; a human breaks it, watches the case go red and restores it ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] The issue's test command stays green with text after the verdict working as today ⟦full-suite⟧

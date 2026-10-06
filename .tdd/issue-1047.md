# Plan for #1047 — preserve-attempt.sh still names an attempt per the locale's charset under a non-UTF-8 locale

- [x] For a step argument "a—b" that reaches preserve-attempt as a non-UTF-8 locale's decoding of its UTF-8 bytes (simulated by injecting the decoded argv and that locale's filesystem encoding), the ref name and the .tdd/attempts/ file name are byte-identical to those written for the same step under LC_ALL=C and under a UTF-8 locale ⟦criterion 1⟧
- [ ] The #1032 locale case in tests/py/test_preserve_attempt.py, which pins the UTF-8 and C names to #1046's one-dash-per-character rule, stays unchanged and green ⟦diff-checked⟧ ⟦criterion 2⟧

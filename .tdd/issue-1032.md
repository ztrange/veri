# Plan for #1032 — preserve-attempt.sh names the attempt ref differently depending on the caller's locale

- [x] The locale-rule case in tests/py/test_preserve_attempt.py changes to the locale-independent rule: for the step argument "a—b ⟦x⟧/c'd" the ref name and the .tdd/attempts/ file name preserve-attempt writes are byte-identical under LC_ALL=C, LC_ALL=en_US.UTF-8, LC_ALL=en_US, and with none of LC_ALL/LC_CTYPE/LANG set ⟦criterion 1⟧
- [x] For a step argument holding multi-byte UTF-8 characters, '/', an apostrophe and spaces, the ref preserve-attempt.sh creates is accepted by git check-ref-format ⟦criterion 2⟧
- [x] The existing contract cases in tests/preserve-attempt.test.sh and tests/py/test_preserve_attempt.py stay unchanged and green, the locale-rule case alone excepted ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 4⟧

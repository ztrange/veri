# Plan for #1030 — preserve-attempt.sh exits 1, not 2, when run outside a git work tree

- [x] Run from a directory that is not inside a git work tree, preserve-attempt.sh <issue> <step> <phase> <attempt> exits 2 (the existing case pinning exit 1 there changes to 2) ⟦criterion 1⟧
- [ ] Outside a git work tree, preserve-attempt.sh prints exactly one stderr line, naming preserve-attempt.sh and saying it is not in a git work tree (git's own fatal line suppressed), creates no scratch directory and runs no git add ⟦criterion 2⟧
- [ ] Inside a work tree, behaviour is unchanged: the existing contract cases in tests/preserve-attempt.test.sh and tests/py/test_preserve_attempt.py stay green ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 4⟧

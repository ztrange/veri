# Plan for #4556 — coupling.sh reports a pair as mutual when each file only holds the other's stem as a word, filing junk refactor-owed issues

- [x] coupling.sh prints no pair, exit 3, when one file only holds the other's stem in a docstring, a comment, a variable, parameter or attribute name, or a string literal, the other importing it ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧
- [x] coupling.sh still prints `mutual: <a> <b>` for two files each invoking the other's script by path ⟦criterion 4⟧
- [ ] affected-suites.sh still selects a test file that holds a changed file's stem only in a comment or a string literal ⟦criterion 5⟧
- [ ] SCRIPTS.md's coupling.sh entry, its row SC389 and veri/README.md say a pair is an import or a by-path invocation each way; SCRIPTS.md regraded

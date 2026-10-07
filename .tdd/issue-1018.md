# Plan for #1018 — refactor-owed.sh render prints a bare ## Refactor owed heading when nothing is owed, and a doubled blank line before Test-only/Applied

- [x] For an owed file whose every step entry was applied or is test-only, refactor-owed.sh render prints `## Refactor owed`, one blank line, then the first `###` subsection, with no second blank line between them ⟦criterion 1⟧
- [x] For an owed file with no step entries, no test-only transforms and no applied transforms, including one whose step headings all had their entries applied, refactor-owed.sh render prints nothing and exits 0 ⟦criterion 2⟧
- [ ] For an owed file with at least one step entry left, refactor-owed.sh render prints the same bytes as before this change ⟦criterion 3⟧
- [ ] refactor_owed.py reads `out = ` with a space before `=` ⟦diff-checked⟧ ⟦criterion 4⟧

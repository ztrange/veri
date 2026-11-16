# Plan for #4046 — PRD 025.6: a ratchet on test files that define their own git helper

- [ ] a test file under tests/py that defines a module-level git or _git function and is not in the list fails a case naming it, repo_builder.py exempt; the list holds every such file today, sorted, one per line with a reason, and the docstring says new cases use repo_builder.git and a function-local helper is outside the rule ⟦criterion 1⟧ ⟦criterion 2⟧
- [ ] a listed file that no longer defines one fails a case naming it ⟦criterion 1⟧

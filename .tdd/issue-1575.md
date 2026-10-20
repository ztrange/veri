# Plan for #1575 — Refactor owed by #1547

- [ ] Substitute Algorithm: `main()` in `skills/tdd/scripts/veri/rebase_onto_default.py` computes `callers` by calling `rebase_in_progress()` instead of its own inline `any(pathlib.Path(path).is_dir() for path in output("rev-parse", "--git-path", "rebase-merge", "--git-path", "rebase-apply")…)`, so the module checks the two rebase directories in one place; predicate, false before and true after: `grep -q 'callers = rebase_in_progress()' skills/tdd/scripts/veri/rebase_onto_default.py && [ "$(grep -c 'rebase-merge' skills/tdd/scripts/veri/rebase_onto_default.py)" = 1 ]` ⟦criterion 2⟧
- [ ] Behaviour unchanged: every existing case keeps its name and outcome ⟦full-suite⟧ ⟦criterion 1⟧

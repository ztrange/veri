# Plan for #2374 — merge-lock.sh gate with no command prints its usage line, not a traceback

- [x] `merge-lock.sh gate --pid 1` (no `--` and no command) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `merge-lock.sh gate --pid 1 --` (a `--` with no command after it) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧

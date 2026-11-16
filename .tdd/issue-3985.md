# Plan for #3985 — PRD 021.6: `make test` reports a broken test runner as exit 2

- [x] with `full_run_lock.acquire` raising `OSError`, the leg exits 2 with one stderr line naming the exception in `entry.refusal`'s form, no traceback ⟦criterion 1⟧
- [x] a leg whose passes ran and had a failing case still exits 1 through the same entry ⟦criterion 2⟧
- [ ] the bytecode-cache record still runs after such an exit 2 ⟦criterion 3⟧
- [ ] CLAUDE.md's Testing idiom refusals paragraph says an error escaping the leg is exit 2 (CM158), graded ⟦criterion 4⟧

# Plan for #155 — make docs-test fails a docs suite that never reached its count line, even when it exits 0

- [ ] `make -C projects/docs test` fails and names a fixture suite that runs one case, then references an unbound variable under `set -u` and exits 0 ⟦criterion 1⟧
- [ ] a fixture suite ending in its count line with `0 failed` and exit 0 still passes `make -C projects/docs test` ⟦criterion 2⟧
- [ ] a fixture suite that prints a non-count last line and exits 3 is reported as nothing to do, not as a suite that never reached its count line, and does not fail the target ⟦criterion 2⟧
- [ ] a second suite added under `projects/docs/tests/` beside an existing one is checked by the unedited runner: it is named when it never reaches its count line ⟦criterion 3⟧

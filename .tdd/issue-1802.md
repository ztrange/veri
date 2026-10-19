# Plan for #1802 — test_dead_libraries.py counts a library named only by another dead library as live, and does not read docs/hooks

- [ ] The dead-library guard in test_dead_libraries.py reports, by name, both `lib/a.sh` and `lib/b.sh` when `lib/a.sh` is named only by `lib/b.sh` and nothing outside `lib/` names `lib/b.sh` (a fixture tree under tmp_path, a small case: no process) ⟦criterion 1⟧
- [ ] The dead-library guard reports nothing for `lib/a.sh` and `lib/b.sh` when an entry point outside `lib/` names `lib/b.sh` and `lib/b.sh` names `lib/a.sh` (a fixture tree under tmp_path, a small case: no process) ⟦criterion 1⟧
- [ ] The dead-library guard reads `docs/hooks/reference-transaction`: a library named only by that hook is not reported dead (a fixture tree under tmp_path, a small case: no process) ⟦criterion 2⟧
- [ ] Each new case is watched to fail with its fix reverted, then restored ⟦human-owed⟧ ⟦criterion 3⟧

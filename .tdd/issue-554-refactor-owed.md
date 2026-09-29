### a projects/docs/Makefile exists, so the copied scripts and suites that call make from projects/docs/ resolve ⟦added⟧ ⟦criterion 1⟧
- make the guard a shared prerequisite instead of repeating `@$(DEV_RUN_GUARD)` in `docs`, `test` and `fresh`. No test requires it, so I left it.

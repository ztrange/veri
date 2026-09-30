# Plan for #582 — make test's symlinked binary on macOS finds no templates or exec-path: fixture repos have no info/ or hooks/

- [x] `make test` gives every suite a GIT_EXEC_PATH equal to what the resolved real git reports for `--exec-path` when run at its own path, not the path the symlink derives ⟦criterion 1⟧
- [ ] `make test` gives every suite a GIT_TEMPLATE_DIR naming the templates directory beside the resolved real git (`../share/git-core/templates`) when that directory exists, and leaves it unset when it does not (the Linux path) ⟦criterion 2⟧

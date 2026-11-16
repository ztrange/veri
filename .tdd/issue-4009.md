# Plan for #4009 — PRD 024.12: a leaf loads no CLAUDE.md from above its working tree

- [ ] launched in a git working tree, a leaf's `--settings` `claudeMdExcludes` holds the global entry, then `CLAUDE.md` and `CLAUDE.local.md` in every directory above its top level up to the root, and not the top level's own ⟦criterion 1⟧ ⟦criterion 2⟧
- [ ] launched where `git rev-parse --show-toplevel` fails, a leaf's `claudeMdExcludes` is the global entry alone ⟦criterion 3⟧
- [ ] `context_limits()` called with no argument, as the conductor's launch calls it, names the global `CLAUDE.md` alone ⟦criterion 4⟧

# Plan for #4009 — PRD 024.12: a leaf loads no CLAUDE.md from above its working tree

- [x] launched in a git working tree, a leaf's `--settings` `claudeMdExcludes` holds the global entry, then `CLAUDE.md` and `CLAUDE.local.md` in every directory above its top level up to the root, and not the top level's own ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] launched where `git rev-parse --show-toplevel` fails, a leaf's `claudeMdExcludes` is the global entry alone ⟦criterion 3⟧
- [x] the conductor launched inside a git working tree still names the global `CLAUDE.md` alone in its `claudeMdExcludes` ⟦criterion 4⟧

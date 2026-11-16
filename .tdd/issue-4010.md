# Plan for #4010 — PRD 024.4: grader leaves load no project CLAUDE.md

- [x] the grader leaf `grade_prose.grade_unit` launches carries, in its `--settings` `claudeMdExcludes`, `CLAUDE.md` and `CLAUDE.local.md` in its working directory, beside the global entry ⟦criterion 1⟧
- [ ] a leaf launched without the grader's request (every `develop-*`, `revise-*`, `verify-*` and `adjudicate-*` leaf) does not exclude its working directory's `CLAUDE.md` or `CLAUDE.local.md` ⟦criterion 2⟧
- [ ] `grade_prose.signature` returns the value it returned before this issue for a pinned unit, rows and model ⟦criterion 4⟧

# Plan for #4024 — PRD 027.13: the run's start after preflight is one call

- [x] `run-start.sh <n>` follows the port convention: usage and exit 2 with no argument, a missing `.tdd/issue-<n>-preflight` exit 2 before any inner call ⟦criterion 9⟧
- [x] it runs `leaf-timeout.sh`, `capture-spec.sh`, `ensure-run-state-ignored.sh` and on `added` the `.gitignore` commit, in the worktree and in order, each printed, any non-zero exit stopping it ⟦criterion 1⟧ ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧
- [ ] a tree listing anything but `.gitignore` before the commit stops it at `1.4 tree-check` ⟦criterion 3⟧
- [ ] on a resume it runs `plan-reverify.sh` and prints `verify_plan=` ⟦criterion 2⟧
- [ ] exit 0 writes and prints `.tdd/issue-<n>-run-start`; no comment on either path ⟦criterion 4⟧ ⟦criterion 5⟧
- [ ] a guard fails when an inner call is a `$S/` script `SKILL.md` step 1 does not name ⟦criterion 10⟧
- [ ] docs: `SKILL.md` step 1, `SCRIPTS.md`, rows and grades ⟦criterion 11⟧ ⟦criterion 12⟧

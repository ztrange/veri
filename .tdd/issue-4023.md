# Plan for #4023 — PRD 027.2: a resumed run's preflight is the same one call

- [x] a worktree holding a ledger after `issue-worktree.sh` takes the resume path: no exit 2, no `unlabel-issue.sh`, the ledger passed to `requirements-preflight.sh` ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] a handed-back worktree runs `resume-clean.sh`, `rebase-onto-default.sh`, the `resume-rebase` event and `rerecord-rebased` after `worktree-setup.sh` ⟦criterion 3⟧
- [x] a rebase that moved the branch is pushed with the pinned lease after a green fast tier, a dirty tree stopping it at `3 tree-check` ⟦criterion 4⟧
- [x] `run=`, `stray=` and `rebased_from=` lines in the preflight file, and before a `stopped at` line ⟦criterion 5⟧
- [x] called again after an exit 3 it repeats none of the handed-back calls and still reports their values ⟦criterion 6⟧
- [x] the wait record names its conductor; under another one it is discarded ⟦criterion 7⟧
- [x] a red tier on a resume stops under FP4 with no re-run, checkout or `suite-red-resume.sh` ⟦criterion 8⟧
- [x] resume cases beside the fresh ones for output, stops, waits, reuse, file and events ⟦criterion 9⟧
- [x] a guard fails when a handed-back call of `PREFLIGHT.md` step 3 is missing from the script's ordered list ⟦criterion 10⟧
- [x] docs: `SKILL.md` step 0, `PREFLIGHT.md`, `RESUME.md` sub-step 2, `SCRIPTS.md`, rows and grades ⟦criterion 11⟧ ⟦criterion 12⟧

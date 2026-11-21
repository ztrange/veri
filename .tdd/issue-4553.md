# Plan for #4553 — A conflicted rebase resolved by develop-rebase leaves .tdd/issue-<n>-branch-base on the old base

- [x] `rebase-onto-default.sh --resolved <onto-sha>`, run on a run's branch after a conflicted rebase was resolved onto `<onto-sha>`, re-records `.tdd/issue-<n>-branch-base` as `<onto-sha>` and exits 0 ⟦criterion 1⟧
- [x] `rebase-onto-default.sh --resolved <onto-sha>` exits 2 and leaves the record untouched when HEAD does not contain `<onto-sha>` or it is not a hex commit name
- [ ] `rebase-onto-default.sh --resolved <onto-sha>` prints, on stdout, the sha the record held before it re-recorded it (nothing when there was none), so the reset path can restore the run's base
- [ ] DRAFT-PR.md's conflict path runs `rebase-onto-default.sh --resolved <onto-sha>` once the develop-rebase leaf has resolved, before the regrade block and verify-rebase (exit 2 bails `no-verdict`); SCRIPTS.md documents the flag; rows added and the units regraded ⟦criterion 1⟧

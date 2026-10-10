# Plan for #1420 — A resumed run's stray capture can be overwritten, and an untracked stray file blocks its rebase

- [x] SKILL.md's Resume sub-step 2 says the stray capture already happened in preflight step 3 and uses that `$stray`; it never tells the conductor to run `stray="$(git status --porcelain)"` again after the reset, pinned by a prose case that goes red if sub-step 2 re-captures ⟦criterion 1⟧
- [x] On a resume whose worktree holds an untracked file a killed leaf left at a path the default branch has since added, preflight's discard removes it after capturing `$stray`, so `rebase-onto-default.sh` then exits 0 instead of 2, pinned by a case that goes red without the removal ⟦criterion 2⟧
- [ ] The untracked stray file is listed in the `$stray` value captured before the removal, the list the ▶️ Resuming comment names ⟦criterion 2⟧
- [ ] Preflight's discard never removes files ignored by `.gitignore` — a `.tdd/` run-state file such as the ledger's leaf logs survives it ⟦criterion 2⟧

# Plan for #4263 — A verifier's run line comes from the working tree's CLAUDE.md, which a developer leaf can edit

- [x] Outside veri's own tree, `build-verify-prompt.sh --branch-base <sha>` renders the base commit's `veri: one test file:` run lines when the working tree's line changed after it, uncommitted or committed on the branch ⟦criterion 1⟧
- [x] Outside veri's own tree, with no `veri: one test file:` line at the `--branch-base` commit and one added on the branch, `build-verify-prompt.sh` renders the base commit's all-tier fallback ⟦criterion 2⟧
- [x] Outside veri's own tree, a `--branch-base` git cannot resolve to a commit is refused (exit 2, one stderr line), never answered from the working tree's `CLAUDE.md`
- [x] Outside veri's own tree, `verify.sh` passes the merge base of HEAD and origin/HEAD as the branch base for every phase, and exits 2 naming the missing merge base when there is none
- [ ] `build-verify-prompt.sh`'s usage line and the catalogue name `--branch-base <sha>`, its only base input, refused unless it matches `^[0-9a-f]{7,40}$` ⟦criterion 3⟧

# Plan for #3120 — A case deleted by uncommitted supersede edits is not reported by deleted_cases

- [ ] On the supersede-diff route (verify's `diff` phase run with `--supersede-base <git stash create snapshot>`), a pytest case an earlier step added that the uncommitted working-tree edits delete — still present in HEAD — is reported by `deleted_cases` (the working tree compared with that snapshot), so verify exits 1 naming it as a deleted case, the same as a committed deletion ⟦criterion 1⟧
- [ ] Guard's go-red: with the working-tree comparison broken on purpose (compare against HEAD only), the case pinning the uncommitted supersede deletion goes red; restored afterwards ⟦human-owed⟧ ⟦criterion 2⟧

# Plan for #2372 — Queued merges run from the repo on merge-lock.sh, releasing the lock on red CI as veri-merge does

- [x] A queued merge, `queued-merge.sh <pr> <worktree> <branch> <tag-message|->` (a new /bin/sh shim over a new veri/queued_merge.py module, listed in SCRIPTS.md, exiting 2 with a usage line naming it when called with no argument), that rebases and pushes cleanly but is stopped by red CI exits 1 and leaves the merge lock free, so a second queued merge takes it at once; gh and git faked ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A queued merge stopped by a rebase conflict onto origin/main exits 1 and keeps the merge lock held; gh and git faked ⟦criterion 1⟧
- [ ] A queued merge whose push under the pinned lease is refused exits 1 and keeps the merge lock held; gh and git faked ⟦criterion 1⟧
- [ ] A queued merge whose CI is green on the pushed head rebase-merges the PR matching that head, deletes the remote branch, removes the worktree, and exits 0 with the merge lock free; gh and git faked
- [ ] A queued merge whose merge does not land (gh refuses it, or the PR's state is not MERGED afterwards) exits 1 and leaves the merge lock free; gh and git faked
- [ ] After a confirmed merge a queued merge cuts the next vN.M tag (by git tag --sort=-v:refname) on origin/main annotated with the tag message and pushes it, and cuts no tag when the message is '-'; gh and git faked
- [ ] A queued merge takes the lock through `merge-lock.sh take --pid <its pid>`, so a lock left by a dead holder is reported on stderr naming that holder ⟦criterion 2⟧

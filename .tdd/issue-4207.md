# Plan for #4207 — PRD 034.3c: stack-fix.sh pushes a reviewed hand fix on a red stack, once per culprit

- [x] stack-fix.sh pushes a fix worktree's HEAD to the stack under the merge lock when <red-sha> is the red commit and every check holds, printing the pushed sha; a <red-sha> not the commit stack-red.sh prints is exit 1 ⟦criterion 1⟧
- [x] exits 1 when <n> or <red-sha> is not what <culprit-file> records ⟦criterion 2⟧
- [x] exits 1 when the stack already carries a Stack-fix commit of <n> ⟦criterion 3⟧
- [x] exits 3 on stack-red.sh exit 3 and 2 on no answer from stack-red.sh, git or GitHub ⟦criterion 4⟧
- [x] exits 1 on a fix commit without the (#<n>) subject or the Stack-fix trailer, or a fetched stack that is not an ancestor of HEAD ⟦criterion 5⟧
- [x] a push refused because origin's stack moved is exit 1, never forced ⟦criterion 6⟧
- [x] a test file added, changed, deleted or renamed is exit 1 naming it ⟦criterion 7⟧
- [x] each named case runs alone at HEAD: red, absent or not collected is exit 1, no answer exit 2 ⟦criterion 8⟧
- [x] a red fast tier or prose-owed.sh non-zero is exit 1 ⟦criterion 9⟧
- [x] every exit 1 or 2 frees the lock, pushes nothing and keeps the fix worktree ⟦criterion 10⟧
- [ ] after the push it comments once on the tracking pull request and once on issue <n> ⟦criterion 11⟧
- [ ] it calls no wait-ci.sh and lifts no freeze, pinned by a spy on its script calls ⟦criterion 12⟧
- [ ] the shim, the module index entry and a process case ⟦criterion 13⟧
- [ ] the module names no repository, issue or job ⟦criterion 14⟧
- [ ] SCRIPTS.md lists stack-fix.sh, row SC257, graded ⟦criterion 15⟧

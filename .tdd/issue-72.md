# Plan for #72 — Keep the caller's checkout clean after the run-state rule is committed only on the issue branch

- [x] ensure-run-state-ignored.sh also writes veri's run-state rule into the repo's shared info/exclude, so the primary checkout's git status is empty while the worktree at .tdd/wt/n exists
- [x] the worktree still ignores .tdd/develop-red.log and still does not ignore the ledger .tdd/issue-n.md, unchanged by the exclude-file fix
- [x] a second run against the same repo leaves both the worktree .gitignore and info/exclude byte-identical and exits 0
- [x] SKILL.md step 1.4 and the walkthrough describe the shared exclude file as what keeps .tdd/wt/n out of the caller's git status

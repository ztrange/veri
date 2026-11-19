# Plan for #4410 — PRD 033.3: on recovery the outage's offline joins reach GitHub and the stack lands

- [x] stack-recover.sh is a /bin/sh shim over veri/stack_recover.py; an argument is exit 2 with its usage ⟦criterion 1⟧
- [x] stack-recover.sh exits 2 while .tdd/github-outage exists, before any read ⟦criterion 2⟧
- [x] stack-recover.sh exits 3 when stack-branch.sh exits 3, and 2 when it exits 2 ⟦criterion 2⟧
- [x] stack-recover.sh takes the merge lock and fetches; a failed take or fetch is exit 2, the lock freed ⟦criterion 3⟧
- [x] stack-recover.sh exits 3 when the local stack is absent, is origin/<stack>, or is behind it, the lock freed ⟦criterion 3⟧
- [ ] stack-recover.sh exits 1 naming both shas when origin/<stack> is not an ancestor of the local stack, nothing pushed ⟦criterion 4⟧
- [ ] stack-recover.sh pushes each Veri-Joined commit to its branch oldest first under a lease on origin/<branch> as fetched; a refused lease is exit 1 naming the branch, the stack not pushed ⟦criterion 5⟧
- [ ] stack-recover.sh then pushes the stack under a lease on origin/<stack> as fetched, never --force ⟦criterion 6⟧
- [ ] stack-recover.sh re-reads each joined PR over the settle window; one not reading merged is exit 2 naming it, the stack left as pushed ⟦criterion 7⟧
- [ ] stack-recover.sh deletes each joined run's remote branch and refs/veri/runs/<n>, runs stack-pr.sh and on exit 0 prints <tip-sha> <tracking-pr-url> ⟦criterion 8⟧
- [ ] stack-recover.sh exits 2 when stack-pr.sh exits 2 or 3, naming it, the push and cleanup kept
- [ ] a real-git process case recovers two offline joins end to end against a bare origin
- [ ] stack-land.sh's slice PR body gains one line per Veri-Suite: skipped commit in its range and one naming .tdd/stack-local-red when it exists ⟦criterion 9⟧
- [ ] voutage SKILL.md and SCRIPTS.md say what VO10, VO7 and SC598 say, graded ⟦criterion 10⟧
- [ ] nothing touched names a repository, issue, branch, label or person ⟦criterion 11⟧

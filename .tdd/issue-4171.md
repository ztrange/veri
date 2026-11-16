# Plan for #4171 — PRD 034.1c: a reviewed run joins the stack branch with no CI wait and no merge call

- [x] queued-merge.sh joins a pull request whose base is the stack: lock, fetch, rebase onto origin/<stack>, leased push of the run's branch, fast tier and prose-owed.sh on the rebased tip, push of that tip to <stack> ⟦criterion 1⟧
- [x] a stack push refused because origin's stack moved starts the join again from the fetch, never forced, the stack ending with both writers' commits ⟦criterion 2⟧
- [x] a join makes no wait-ci.sh call and no merge call, cuts no tag and closes no issue ⟦criterion 3⟧
- [x] after the stack push the join re-reads the pull request over the settle window: a merged read exits 0, none exits 2 naming the last state read ⟦criterion 4⟧
- [x] a join whose ledger's only unticked line is ⟦full-suite⟧ goes ahead; any other unticked line exits 1 before anything is pushed to the stack ⟦criterion 5⟧
- [x] a rebase conflict exits 1, nothing pushed to the stack, the merge lock released ⟦criterion 6⟧
- [x] a red fast tier exits 1, nothing pushed to the stack, the merge lock released ⟦criterion 6⟧
- [x] a prose-owed.sh exit 1 exits 1, nothing pushed to the stack, the merge lock released ⟦criterion 6⟧
- [x] a join that gets no answer (no fast-tier command, a rebase refused without a conflict, a stack name that cannot be one, an error raised mid-join) exits 2 and releases the merge lock
- [x] solvable-issues.sh does not list an open issue a pull request merged into the stack closes ⟦criterion 7⟧
- [ ] issue-worktree.sh refuses, exit 2, an issue a pull request merged into the stack closes, with no open pull request naming it ⟦criterion 7⟧
- [ ] after a join's exit 0 the run's remote branch is deleted and its worktree removed, the main clone not moved ⟦criterion 8⟧
- [ ] where no stack branch is named, queued-merge.sh merges as before and solvable-issues.sh and issue-worktree.sh read open pull requests only ⟦criterion 9⟧
- [ ] no added skill line and nothing in stack_branch.py names a repository, issue, branch, label or person ⟦criterion 10⟧
- [ ] SCRIPTS.md's queued-merge.sh, solvable-issues.sh and issue-worktree.sh entries state the join and the joined claim (SC198, SC199, SC200), graded ⟦criterion 11⟧
- [ ] /vmerge says a reviewed run is joined, not merged, where a stack is named, the review being the gate, what a join does not do, and the ⟦full-suite⟧ precondition (M31, M32, M33), graded ⟦criterion 12⟧

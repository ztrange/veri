# Plan for #4197 — PRD 034.3a: a join to the stack is refused while CI's latest answer on it is red

- [x] a join runs stack-red.sh after its fetch and before its rebase; on its exit 0 the join exits 1, nothing rebased or pushed, the lock freed, the run's worktree and branch kept ⟦criterion 1⟧
- [x] the refusal is one stderr line naming the red commit, its run's url and stack-culprit.sh <sha> as the next command ⟦criterion 2⟧
- [x] a stack-red.sh exit 2, or any exit but 0 and 3, is the join's exit 2, nothing pushed, the lock freed ⟦criterion 3⟧
- [x] a stack-red.sh exit 3 lets the join proceed, and with each of the join's own knobs set an exit 0 is still exit 1 ⟦criterion 4⟧
- [x] a merge where no stack is named makes no stack-red.sh call ⟦criterion 5⟧
- [x] the code this issue adds names no repository, issue, branch, label or person ⟦criterion 6⟧
- [x] SCRIPTS.md's queued-merge.sh entry states the freeze (SC251), graded ⟦criterion 7⟧
- [x] skills/vmerge/SKILL.md says a frozen join is retried once the stack is green and stack-culprit.sh <sha> is the next step (M35), graded ⟦criterion 8⟧

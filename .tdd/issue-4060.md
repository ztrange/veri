# Plan for #4060 — PRD 020.12: one writer per worktree

- [x] skills/vmerge/SKILL.md *Preconditions* lists no process inside the run's worktree (lsof +D <worktree>), a failed check stopping the merge; row M29, graded PASS ⟦criterion 1⟧
- [x] skills/vdev/SKILL.md *No closing comment*: the resume runs only when no process is inside the run's worktree, else held to the next slot decision; row D66, graded PASS ⟦criterion 2⟧

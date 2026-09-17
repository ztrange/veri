# Plan for #237 — A live run executes whatever skills/tdd/ holds when each script is called, so a merge pulled mid-run changes its scripts under it

- [x] A conductor launched by `run-conductor.sh` (stub `CLAUDE_BIN`) receives a base directory that is not the primary clone's `skills/tdd`, and whose files are the skill commit recorded for the run
- [x] Changing or deleting a script in the primary clone after launch does not change what the run's leaves execute: `supervise.sh`, `run-leaf.sh` and the prompt templates a leaf is built from are read from the snapshot
- [x] A resume of that run uses the recorded commit, re-materialising the snapshot if it was removed
- [x] A resume on which the operator explicitly asks for the new skill pins the current commit instead, and records that re-pin as an event in the run's event log ⟂ refactor pending
- [ ] With no resolvable commit the run proceeds unpinned and a warning is printed on stderr
- [ ] The snapshot is ignored run state: `git status --porcelain` in the worktree and in the caller's checkout stays empty

# Plan for #3707 — pin-recheck.sh replays every mutation past the leaf cap and leaves the mutation applied when killed

- [x] pin-recheck.sh does not re-replay a mutation record already shown red at the same tree state, and replays it again once that state changes: in one case, a second run at an unchanged tree and record runs none of that record's test commands again and still exits 0, while a run after the mutated file's bytes change, and a run after HEAD moves, each replay it again ⟦criterion 1⟧
- [x] A SIGTERM sent to pin-recheck.sh mid mutation replay leaves the worktree as it was before the replay: the mutated file holds its original bytes after the process exits ⟦criterion 2⟧
- [x] A SIGINT sent to pin-recheck.sh mid mutation replay leaves the worktree as it was before the replay: the mutated file holds its original bytes after the process exits

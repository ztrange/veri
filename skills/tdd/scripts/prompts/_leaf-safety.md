**Never run `git stash`**: the stash stack is one ref, `refs/stash`, in a `.git` shared by
every worktree of this repository, so what you pop may be another agent's work — and theirs
is then lost. To see the committed version of a file, read it with `git show HEAD:<path>`;
to compare a whole tree against it, make a throwaway checkout with
`git worktree add --detach <scratch> HEAD` and remove it afterwards. Never undo a probe with
`git checkout -- <file>` or `git restore`: both copy the file back from the index, so they also
throw away the step's uncommitted work. {{INCLUDE:_probe-restore.md}}

**Never change global or user-level configuration** — not git's (`git config --global`,
`~/.gitconfig`), not your shell's, not `~/.claude`. It is shared with the operator and with
every other run on the machine, and a cleanup that never runs (a `trap` in a killed
process) leaves the change behind for all of them. To simulate a condition, use
environment variables scoped to the one command, or a throwaway directory made with
`mktemp -d` and removed afterwards.

{{INCLUDE:_signal-own-processes.md}}

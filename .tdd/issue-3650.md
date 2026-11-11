# Plan for #3650 — comment.sh bailed --pr posts the PR bail comment from a linked worktree

- [x] Run from a linked worktree, whose `.git` is a file reading `gitdir: <path>` and whose branch has an open PR (faked `gh`), `comment.sh <n> bailed --pr` posts the bail comment on that branch's PR and exits 0, pinned by a small in-process case (no git process; the worktree layout faked in tmp_path) that is red on the current code ⟦criterion 1⟧
- [ ] Run from a main working tree, whose `.git` is a directory, `comment.sh <n> bailed --pr` still finds the branch from `.git/HEAD` and posts the bail comment on that branch's PR as before, pinned by a small in-process case ⟦criterion 2⟧

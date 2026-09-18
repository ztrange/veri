# lib/main-working-tree.sh — sourced, not run: defines `main_working_tree`, the one place the
# #166 resolution rule lives for status.sh and solvable-issues.sh.
#
# The main working tree is where issue-worktree.sh puts every run's worktree (`wt_path`, off
# `main_working_tree`) — never the checkout the caller happens to have been called from, which
# for a conductor started inside a session worktree is a different directory entirely (#166).
# git's registry prints the main working tree as the first block's `worktree <path>` line, so
# that first line with its label taken off is the answer.
#
# `|| true` because a caller outside any repository is not an error here: git says nothing and
# the root comes out empty, which each caller reads as "no worktree holds a run".
#
# Taking the label off is inside the function, not a second assignment to a name in the caller's
# own scope, for the reason issue-worktree.sh:37-40 argues about the same two steps.
main_working_tree() {
  local first_line
  first_line="$(git worktree list --porcelain 2>/dev/null | head -n 1 || true)"
  printf '%s\n' "${first_line#worktree }"
}

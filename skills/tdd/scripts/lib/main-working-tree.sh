#!/usr/bin/env bash
# lib/main-working-tree.sh — sourced, not run: defines `main_working_tree`.
#
# main_working_tree — print the repository's main working tree, or an empty line outside one.
#
# hazard: `|| true` is load-bearing under pipefail: outside a repository git fails and the answer is empty.
main_working_tree() {
  local first_line
  first_line="$(git worktree list --porcelain 2>/dev/null | head -n 1 || true)"
  printf '%s\n' "${first_line#worktree }"
}

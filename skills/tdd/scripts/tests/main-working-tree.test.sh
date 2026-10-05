#!/usr/bin/env bash
# Unit tests for scripts/lib/main-working-tree.sh — the one definition of `main_working_tree`.
#
# Contract under test:
#   source lib/main-working-tree.sh; main_working_tree   → the main working tree's path, as
#                                                          git prints it, from a linked worktree
#
# Run: scripts/tests/main-working-tree.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
SCRIPTS="$HERE/.."
HELPER="$SCRIPTS/lib/main-working-tree.sh"
work="$(scratch_dir)"

main_repo="$work/main"
new_repo -b main "$main_repo" >/dev/null 2>&1
git -C "$main_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1
linked="$work/linked"
git -C "$main_repo" worktree add -q -b side "$linked" main >/dev/null 2>&1
first_line="$(head -n 1 < <(git -C "$main_repo" worktree list --porcelain))"
want_main="${first_line#worktree }"

problems=()

got_main="$(cd "$linked" && source "$HELPER" 2>/dev/null && main_working_tree 2>/dev/null)"
[[ -n "$want_main" && "$got_main" == "$want_main" ]] \
  || problems+=("sourcing $HELPER from a linked worktree: main_working_tree printed '$got_main', want '$want_main'")

report "a shared lib/main-working-tree.sh defines main_working_tree, and solvable-issues.sh resolves the main working tree through it"

finish

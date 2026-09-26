#!/usr/bin/env bash
# rebase-onto-default.sh — rebase the run's branch onto origin/<default> before its PR is
# marked ready, when the default branch moved while the run worked (issue #238).
#
# Usage:   rebase-onto-default.sh          # run from the issue's worktree
#
# Exit 3 — nothing to do — when the branch already contains origin/<default>: there is no
# rebase to make, so HEAD and the working tree are left exactly as they were.
#
# Exit 0 when the branch was behind and the rebase applied cleanly: stdout is two lines, the
# pre-rebase sha and then the onto sha, so a caller can name both ends of what moved.
#
# Exit 1 when the rebase conflicts: it is aborted, so HEAD is back at the pre-rebase sha with
# a clean tree and no rebase in progress, and stdout is the conflicting files, one per line.

# main — the whole script. Its logic lives behind this function so a unit suite can source
# the file and run nothing (#339); executed directly, the guard at the bottom calls it.
main() {
  set -uo pipefail

  # The default branch is whatever the remote says it is — origin/HEAD, which a clone
  # records — rather than a name this script assumes.
  local default
  default="$(git rev-parse --abbrev-ref origin/HEAD)"

  git merge-base --is-ancestor "$default" HEAD && exit 3

  local pre onto
  pre="$(git rev-parse HEAD)"
  onto="$(git rev-parse "$default")"
  if ! git rebase -q "$onto" >/dev/null; then
    local conflicts
    conflicts="$(git diff --name-only --diff-filter=U)"
    git rebase --abort
    printf '%s\n' "$conflicts"
    exit 1
  fi
  printf '%s\n%s\n' "$pre" "$onto"
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"

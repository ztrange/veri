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
#
# Exit 2 when git refuses the rebase for any other reason, such as a dirty working tree:
# nothing was started, so HEAD is unchanged and stdout is empty. The same when origin cannot
# be fetched, or a fetch leaves origin/<default> behind the remote's own branch: the local
# copy is stale, so no rebase is attempted onto it.

rebase_in_progress() {
  local d
  for d in rebase-merge rebase-apply; do
    [[ -d "$(git rev-parse --git-path "$d")" ]] && return 0
  done
  return 1
}

main() {
  set -uo pipefail

  local default
  default="$(git rev-parse --abbrev-ref origin/HEAD)"

  git fetch -q origin >/dev/null 2>&1 || exit 2

  # hazard: a fetch that exits 0 need not have refreshed origin/<default>.
  local remote_sha onto
  remote_sha="$(git ls-remote origin "refs/heads/${default#origin/}" 2>/dev/null)" || exit 2
  onto="$(git rev-parse "$default")"
  [[ "${remote_sha%%[[:space:]]*}" == "$onto" ]] || exit 2

  git merge-base --is-ancestor "$onto" HEAD && exit 3

  local pre
  pre="$(git rev-parse HEAD)"
  if ! git rebase -q "$onto" >/dev/null; then
    rebase_in_progress || exit 2
    local conflicts
    conflicts="$(git diff --name-only --diff-filter=U)"
    git rebase --abort
    printf '%s\n' "$conflicts"
    exit 1
  fi
  printf '%s\n%s\n' "$pre" "$onto"
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"

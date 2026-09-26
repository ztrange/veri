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

# rebase_in_progress — succeed when git holds a rebase in progress. Which directory holds it
# depends on the backend: rebase-merge for the merge backend, rebase-apply for
# rebase.backend=apply.
rebase_in_progress() {
  local d
  for d in rebase-merge rebase-apply; do
    [[ -d "$(git rev-parse --git-path "$d")" ]] && return 0
  done
  return 1
}

# main — the whole script. Its logic lives behind this function so a unit suite can source
# the file and run nothing (#339); executed directly, the guard at the bottom calls it.
main() {
  set -uo pipefail

  # The default branch is whatever the remote says it is — origin/HEAD, which a clone
  # records — rather than a name this script assumes.
  local default
  default="$(git rev-parse --abbrev-ref origin/HEAD)"

  # What the clone last fetched may be stale: rebasing onto it would be rebasing onto a
  # guess, so an origin that cannot be fetched is no answer at all — exit 2.
  git fetch -q origin >/dev/null 2>&1 || exit 2

  # A fetch that exits 0 need not have refreshed origin/<default> — a fetch refspec can
  # leave it out — so the remote's own answer for the branch must match what the clone holds.
  local remote_sha
  remote_sha="$(git ls-remote origin "refs/heads/${default#origin/}" 2>/dev/null)" || exit 2
  [[ "${remote_sha%%[[:space:]]*}" == "$(git rev-parse "$default")" ]] || exit 2

  git merge-base --is-ancestor "$default" HEAD && exit 3

  local pre onto
  pre="$(git rev-parse HEAD)"
  onto="$(git rev-parse "$default")"
  if ! git rebase -q "$onto" >/dev/null; then
    # A rebase git refused to start — a dirty tree, say — leaves no rebase in progress.
    # That is no conflict to name: the plumbing failed, so it is exit 2, not 1.
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

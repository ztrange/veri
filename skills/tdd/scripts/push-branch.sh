#!/usr/bin/env bash
# push-branch.sh — copy the run's branch to the remote, from the worktree it runs in.
#
# The conductor calls this at the two points that already write to the ledger: after a
# step's green commit, and after a verify-refactor PASS clears the mark. Until then a run's
# commits live on exactly one disk, and a run interrupted before the draft PR is opened is
# invisible to everyone and recoverable by nobody.
#
# Usage:   push-branch.sh          # run from the issue's worktree
#          push-branch.sh --force-with-lease=<branch>:<sha>
#                                  # replace the remote copy only if it is still at <sha>
#                                  # (publishing a rebase). Never a bare force.
#
# **An unreachable remote is not a bail, so that failure exits 0.** (A non-fast-forward
# rejection is different, and exits 1: see the loop below.) A run
# whose network is down is still a correct run, and the conductor branches on the exit
# code: anything but 0 would stop a methodology that is working for a transport problem.
# The push is a copy, so a failed one owes the run nothing — HEAD, the commit count and the
# ledger are the local run's, untouched by whether the copy landed. What a failure does owe
# is a record, because nothing stops and nothing is narrated as an error: the failure goes
# to `.tdd/events.jsonl` through event.sh, and that line is the only way a human reading the
# run afterwards learns the branch is not on the remote.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/lib/exit-contract.sh"
USAGE="usage: push-branch.sh [--force-with-lease=<branch>:<sha>]"

record() {
  "$HERE/event.sh" "$@" || exit 2
}

main() {
  set -uo pipefail

  local retries backoff tunable attempt out branch remote_sha
  local -a lease=()

  if (( $# > 0 )); then
    if [[ $# -ne 1 || ! "$1" =~ ^--force-with-lease=[^:]+:[0-9a-f]{7,40}$ ]]; then
      refuse "push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, got '$*'"
    fi
    lease=("$1")
  fi

  retries="${VERI_PUSH_RETRIES:-3}"
  backoff="${VERI_PUSH_BACKOFF:-2}"
  # hazard: `(( ))` reads a word as a variable name and a fraction as a syntax error.
  for tunable in "VERI_PUSH_RETRIES=$retries" "VERI_PUSH_BACKOFF=$backoff"; do
    if [[ ! "${tunable#*=}" =~ ^[0-9]+$ ]]; then
      echo "push-branch.sh: ${tunable%%=*} must be a non-negative integer, got '${tunable#*=}'" >&2
      exit 2
    fi
  done
  attempt=0
  while (( attempt <= retries )); do
    attempt=$((attempt + 1))
    if out="$(git push "${lease[@]}" --set-upstream origin HEAD 2>&1)"; then
      exit 0
    fi
    if [[ "$out" == *"[rejected]"* && ( "$out" == *non-fast-forward* || "$out" == *"fetch first"* || "$out" == *"stale info"* ) ]]; then
      branch="$(git rev-parse --abbrev-ref HEAD)"
      remote_sha="$(git ls-remote origin "refs/heads/$branch" | cut -f1)"
      echo "push rejected (non-fast-forward): origin/$branch is at $remote_sha" >&2
      record push-rejected remote_sha="$remote_sha" error="$out"
      exit 1
    fi
    if (( attempt <= retries )); then
      sleep "$backoff"
      backoff=$((backoff * 2))
    fi
  done
  echo "push-branch.sh: push failed after $attempt attempts; the branch is not on the remote" >&2
  record push-failed error="$out" attempts="$attempt"
}

[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"

#!/usr/bin/env bash
# push-branch.sh — copy the run's branch to the remote, from the worktree it runs in
# (issue #191).
#
# The conductor calls this at the two points that already write to the ledger: after a
# step's green commit, and after a verify-refactor PASS clears the mark. Until then a run's
# commits live on exactly one disk, and a run interrupted before the draft PR is opened is
# invisible to everyone and recoverable by nobody.
#
# Usage:   push-branch.sh          # run from the issue's worktree
#          push-branch.sh --force-with-lease=<branch>:<sha>
#                                  # replace the remote copy only if it is still at <sha>
#                                  # (issue #238: publishing a rebase). Never a bare force.
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

# record <event> [key=value…] — append an event, or exit 2 if it cannot be written. A log
# that cannot be written is a system failure, whichever push outcome it was recording.
# event.sh is found beside this script only here, when an event is written, so a unit suite
# that mocks `record` runs main with no `dirname` on PATH.
record() {
  local here
  here="$(cd "$(dirname "$0")" && pwd)"
  "$here/event.sh" "$@" || exit 2
}

# main — the whole script. Its logic lives behind this function so a unit suite can source
# the file and run nothing (#339); executed directly, the guard at the bottom calls it.
main() {
  set -uo pipefail

  local retries backoff tunable attempt out branch remote_sha
  local -a lease=()

  # The one force this script makes is pinned to a sha: a bare `--force` or an unpinned
  # `--force-with-lease` would replace whatever the remote holds, so either is bad arguments.
  if (( $# > 0 )); then
    if [[ $# -ne 1 || ! "$1" =~ ^--force-with-lease=[^:]+:[0-9a-f]{7,40}$ ]]; then
      echo "push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, got '$*'" >&2
      exit 2
    fi
    lease=("$1")
  fi

  # `--set-upstream` so the first call creates the remote branch and later ones fast-forward
  # against it; `HEAD` rather than a branch name so the script reads the branch off the
  # worktree it was run in instead of being told, the way every other conductor script does.
  # The push's own output is kept: it is what says WHY the copy did not land, and a reader of
  # the event log gets no second chance to ask git.
  #
  # A failed push is retried VERI_PUSH_RETRIES more times (extra attempts after the first,
  # the same semantics as VERI_STUCK_RETRIES): an unreachable origin is usually a blip. Only
  # when every attempt has failed does the run hear about it — one stderr line and one event,
  # however many attempts it took. Between attempts the script waits VERI_PUSH_BACKOFF
  # seconds, doubled after each wait (2, 4, 8 by default); none follows the last attempt.
  retries="${VERI_PUSH_RETRIES:-3}"
  backoff="${VERI_PUSH_BACKOFF:-2}"
  # A non-integer tunable is bad arguments, caught before any push: `(( attempt <= retries ))`
  # would otherwise read a word as a variable name and a fraction as a syntax error.
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
    # A ref rejection is not a blip: the remote holds commits HEAD does not, so every retry
    # would fail identically. Name the remote's sha and exit 1 — whether to force or rebase
    # is a judgement, and it belongs to a leaf, not to this script.
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

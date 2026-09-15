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
#
# **A push failure is not a bail, so this script's exit status is 0 either way.** A run
# whose network is down is still a correct run, and the conductor branches on the exit
# code: anything but 0 would stop a methodology that is working for a transport problem.
# The push is a copy, so a failed one owes the run nothing — HEAD, the commit count and the
# ledger are the local run's, untouched by whether the copy landed. What a failure does owe
# is a record, because nothing stops and nothing is narrated as an error: the failure goes
# to `.tdd/events.jsonl` through event.sh, and that line is the only way a human reading the
# run afterwards learns the branch is not on the remote.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# `--set-upstream` so the first call creates the remote branch and later ones fast-forward
# against it; `HEAD` rather than a branch name so the script reads the branch off the
# worktree it was run in instead of being told, the way every other conductor script does.
# The push's own output is kept: it is what says WHY the copy did not land, and a reader of
# the event log gets no second chance to ask git.
if ! out="$(git push --set-upstream origin HEAD 2>&1)"; then
  "$HERE/event.sh" push-failed error="$out"
fi

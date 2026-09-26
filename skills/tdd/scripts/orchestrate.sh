#!/usr/bin/env bash
# orchestrate.sh — the loop above the conductor (issue #217): ask solvable-issues.sh which
# issues veri may take, launch one conductor for the first of them through run-conductor.sh,
# and ask again, until nothing is left to take.
#
# Usage:   orchestrate.sh
#
# It is a script rather than an agent so that its own context stays O(1): an agent looping
# over conductors would accumulate context exactly the way the conductors it launches do.
#
# The solvable set is asked afresh after every launch rather than read once, because a
# finished run leaves the set and that is how the loop learns it finished.
#
# Exit 0 once solvable-issues.sh answers 3 (nothing to take); exit 2, launching nothing, when
# it exits with anything but 0 or 3, since then no answer about the solvable set was obtained.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

while :; do
  issues="$("$HERE/solvable-issues.sh")"
  rc=$?
  [[ $rc -eq 3 ]] && exit 0
  if [[ $rc -ne 0 ]]; then
    echo "orchestrate.sh: solvable-issues.sh exited $rc; no answer about the solvable set" >&2
    exit 2
  fi
  issue="${issues%%$'\n'*}"
  "$HERE/run-conductor.sh" "$issue"
done

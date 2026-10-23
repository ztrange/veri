#!/bin/sh
# coverage-blocker.sh — what a refactor-kind run does when Cover answers `COVERED: no`: a shim over veri/coverage_blocker.py.
#
# Files an unlabelled coverage issue for the refactor issue — no opt-in label, so the queue
# never takes it itself — and names that new issue under the refactor issue's `## Blocked by`
# heading, in place of a `None` line or after the blockers already listed, so
# solvable-issues.sh stops listing the refactor issue until the coverage exists and it cannot
# be retaken only to refuse again.
#
# usage: coverage-blocker.sh <refactor-issue-number>
#   GH_REPO=owner/name coverage-blocker.sh <refactor-issue-number>
#
# Prints the new issue's URL. Exit: 0 on success, 2 on bad arguments. Requires an
# authenticated `gh`, which reads GH_REPO from the environment itself.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/coverage_blocker.py" "$@"

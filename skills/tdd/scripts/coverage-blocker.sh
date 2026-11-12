#!/bin/sh
# coverage-blocker.sh — what a refactor-kind run does when Cover answers `COVERED: no`: a shim over veri/coverage_blocker.py.
#
# Files a runnable coverage issue for the refactor issue and names that new issue under the
# refactor issue's `## Blocked by` heading, in place of a `None` line or after the blockers
# already listed, so solvable-issues.sh stops listing the refactor issue until the coverage
# exists and it cannot be retaken only to refuse again. The filed body has `## Problem`, then
# `## Acceptance criteria` (one `- [ ]` criterion per `MUTATION:` line of the Cover report
# `.tdd/develop-cover.out`, requiring a case that goes red under it; the section is omitted
# when the report has no `MUTATION:` line), then `## Blocked by` with `None.`, and a last line
# `Test command: <the all-tier command>`. Labels: the run's opt-in label (`VERI_LABEL`, default
# `ready-for-agent`) and `filed-by:<lane>` when there are criteria; with no `MUTATION:` line
# only `filed-by:<lane>`, so the queue never takes a criterion-less issue.
#
# usage: coverage-blocker.sh <refactor-issue-number>
#   GH_REPO=owner/name coverage-blocker.sh <refactor-issue-number>
#
# Prints the new issue's URL. Exit: 0 on success, 2 on bad arguments. Requires an
# authenticated `gh`, which reads GH_REPO from the environment itself.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/coverage_blocker.py" "$@"

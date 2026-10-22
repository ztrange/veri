#!/bin/sh
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again: a shim over veri/wait_ci.py.
#
# usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED, not all SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, gh failed, unreadable rollup), a
# check still pending past the deadline an earlier call recorded for the same head commit, or
# checks never started: still queued VERI_CI_QUEUE_WAIT secs after the first call that saw them
# queued · 3 a check is still pending, none has appeared yet, every one was SKIPPED, or the PR
# still reports a head other than <head-sha>, when this call's <slice-seconds> run out.
#
# While every pending check is still queued the deadline does not run. It starts at the first
# call that sees a check in progress for a head commit, <total-seconds> after it (default
# twice the mean of the last 5 CI runs, capped at 600, else 540), and is recorded in
# .tdd/ci-deadline-<sha>; the first queued sighting is recorded in .tdd/ci-queued-<sha>.
#
# Tunables (env): VERI_POLL poll interval secs (default 10); VERI_CI_QUEUE_WAIT secs checks may
# stay queued before exit 2 (default 3600).
exec python3 "$(dirname "$0")/veri/wait_ci.py" "$@"

#!/bin/sh
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again: a shim over veri/wait_ci.py.
#
# usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED, not all SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, a <head-sha> that is not a full 40-hex sha (one stderr line), a read of the checks still failing at the deadline, a 4xx other than
# 403/429 at once), a
# check still pending past the deadline an earlier call recorded for the same head commit, or
# checks never started: still queued VERI_CI_QUEUE_WAIT secs after the first call that saw them
# queued, or a ready, mergeable PR's head with no check run and no commit status for
# VERI_CI_NO_RUN_WAIT secs, counted across calls from the first no-run sighting of the head, while
# a pull_request workflow exists (stderr: no CI run for <sha>)
# · 3 a check is still pending, none has appeared yet, every one was SKIPPED, or the PR
# still reports a head other than <head-sha>, when this call's <slice-seconds> run out.
#
# The deadline does not run only while every pending check is queued (or the PR reports a
# head other than <head-sha>). It is recorded in .tdd/ci-deadline-<sha> by the first call
# where that is not so (a check in progress, no check yet, or only a commit status pending),
# <total-seconds> after it: default twice the mean of the last 5 CI runs, capped at 600; 540
# when fewer than 5 exist or gh cannot answer; the slice length when reading them fails
# otherwise. The first queued sighting is recorded in .tdd/ci-queued-<sha>;
# the first no-run sighting in .tdd/ci-none-<sha>, inherited by later calls for the same sha and
# restarting for a new head.
#
# A failed read is retried, doubling the sleep from VERI_POLL, at most 60 s each.
#
# Tunables (env): VERI_POLL poll interval secs (default 10); VERI_CI_RETRY_BACKOFF 1 (default)
# doubles the retry sleep, 0 keeps it VERI_POLL; VERI_CI_QUEUE_WAIT secs checks may
# stay queued before exit 2 (default 3600); VERI_CI_NO_RUN_WAIT secs, counted across calls from the
# first no-run sighting (.tdd/ci-none-<sha>), a head may have no check run and no status before exit 2 (default 120, a non-negative whole number; anything else exit 2).
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/wait_ci.py" "$@"

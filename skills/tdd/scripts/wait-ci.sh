#!/bin/sh
# wait-ci.sh — wait a bounded slice for a PR's checks to finish, and be called again: a shim over veri/wait_ci.py.
#
# usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]
#
# Status: 0 every check completed SUCCESS, NEUTRAL or SKIPPED, not all SKIPPED · 1 a completed check
# concluded anything else · 2 no answer (bad arguments, gh failed, unreadable rollup), or a
# check still pending past the deadline an earlier call recorded for the same head commit ·
# 3 a check is still pending, none has appeared yet, every one was SKIPPED, or the PR still
# reports a head other than <head-sha>, when this call's <slice-seconds> run out.
#
# The deadline, <total-seconds> (default <slice-seconds>) after the first call for a head
# commit, is recorded in .tdd/ci-deadline-<sha>.
#
# Tunables (env): VERI_POLL poll interval secs (default 10).
exec python3 "$(dirname "$0")/veri/wait_ci.py" "$@"

#!/bin/sh
# status.sh — render every veri run under the repository's main working tree: a shim over veri/status.py.
#
# Runs are discovered from `.tdd/wt/*` under the MAIN working tree, never the checkout this script
# was called from.
#
# Usage:   status.sh [--json] [--scope <name>] [--watch [seconds]]   (no --scope: VERI_LABEL, when set, names the scope)
#          status.sh --report
#          status.sh --recover dev [--lane <lane>]
#          --json prints the same runs and scope totals as one JSON document, and the stack's figures
#          under a stack key where a stack branch is named (not with --watch).
#          --watch redraws in place every <seconds> (default 2), each render recomputed from disk.
#          --report (alone) prints the /vstatus report: Landed, Stack, Running, Queue, Waiting,
#          from local files only, with no gh, where no stack branch is named; Stack (joined, tested
#          and landed counts, the tracking pull request, a freeze; ? for a figure not read) only
#          where one is. A stale snapshot starts a detached cache refresh.
# Exit:    0 one or more runs printed; 2 an unknown option, or no answer; 3 nothing to do — "no runs"
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/status.py" "$@"

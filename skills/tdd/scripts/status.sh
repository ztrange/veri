#!/bin/sh
# status.sh — render every veri run under the repository's main working tree: a shim over veri/status.py.
#
# Runs are discovered from `.tdd/wt/*` under the MAIN working tree, never the checkout this script
# was called from.
#
# Usage:   status.sh [--json] [--scope <name>] [--watch [seconds]]   (no --scope: VERI_LABEL, when set, names the scope)
#          --json prints the same runs and scope totals as one JSON document.
#          --watch redraws in place every <seconds> (default 2), each render recomputed from disk.
#          --report (alone) prints the /vstatus report from local files only, with no gh:
#          Landed, Running, Queue, Waiting. A stale snapshot starts a detached cache refresh.
# Exit:    0 one or more runs printed; 2 an unknown option, or no answer; 3 nothing to do — "no runs"
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/status.py" "$@"

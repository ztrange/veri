#!/usr/bin/env bash
# Tests for scripts/workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns
# issues to named workers and records what happened to each.
#
# Contract under test:
#   workqueue.sh assign <worker> <issue>...  → appends one `<worker>\t<issue>\tqueued\t` line
#                                              per issue to `.tdd/workqueue` in the main
#                                              working tree, in the order given
#   workqueue.sh next <worker>               → prints that worker's first `queued` issue whose
#                                              `## Blocked by` names no open issue, read from
#                                              the VERI_GH_JSON fixtures
#   workqueue.sh start <worker> <issue>      → rewrites that worker's `queued` line for the
#                                              issue to `running`, in place
#   workqueue.sh done <worker> <issue> <sha> → rewrites that worker's `running` line for the
#                                              issue to `merged`, the sha as its detail
#   workqueue.sh park <worker> <issue> <why> → rewrites that worker's `running` line for the
#                                              issue to `parked`, the reason as its detail
#
# Run: scripts/tests/workqueue.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../workqueue.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

finish

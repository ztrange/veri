#!/bin/sh
# ci-flake.sh — the flake check of a red CI run: rerun alone each test target its saved `gh run view --log-failed` log names, and when all pass re-run the failed jobs once: a shim over veri/ci_flake.py.
#
# Usage:   ci-flake.sh <n> <head-sha> <run-id> '<alone-cmd>' <log-file>
# Exit:    0 the re-run was accepted (targets printed); 1 no target, or one stays red alone; 2 no answer or bad arguments; 3 no re-run left for this head or run
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ci_flake.py" "$@"

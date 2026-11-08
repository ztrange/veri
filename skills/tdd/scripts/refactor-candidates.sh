#!/bin/sh
# refactor-candidates.sh — file the one issue listing what a run's structural pass left: a shim over veri/refactor_candidates.py.
#
# usage:   refactor-candidates.sh <issue> <owed-file>
# Exit:    0 the issue's url printed; 2 a bad argument; 3 nothing out-of-bounds or not done (no issue filed)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/refactor_candidates.py" "$@"

#!/bin/sh
# discarded-exit.sh — print each added .py line of `git diff HEAD` whose exit code is discarded: a shim over veri/discarded_exit.py.
#
# Usage:   discarded-exit.sh
# Exit:    0 none printed; 1 one or more <file>:<line> printed; 2 an argument, or no answer; 3 nothing to do — no .py file in the diff
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/discarded_exit.py" "$@"

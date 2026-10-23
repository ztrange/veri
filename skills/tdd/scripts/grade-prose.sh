#!/bin/sh
# grade-prose.sh — grade one prose unit against its requirements list: a shim over veri/grade_prose.py.
#
# usage: grade-prose.sh <requirements-file> <unit>
# Exit:  0 PASS · 1 REJECT · 2 bad arguments, or no verdict could be obtained
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/grade_prose.py" "$@"

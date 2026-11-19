#!/bin/sh
# grade-prose.sh — grade one prose unit against its requirements list: a shim over veri/grade_prose.py.
#
# usage: grade-prose.sh <requirements-file> <unit>
#        | --owed | --convert
#        | --signed <base>   print the units the branch signed since <base>: <requirements-file>, a tab, the unit
#                            decoded, per GRADED line absent at <base>
# Exit:  0 PASS · 1 REJECT · 2 bad arguments, or no verdict could be obtained; --signed: 0 listed (none included),
#        2 git could not read a tree
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/grade_prose.py" "$@"

#!/bin/sh
# coupling.sh — the pairs of code files, one changed in a range, that import or invoke each other: a shim over
# veri/coupling.py.
#
# Prints `mutual: <a> <b>` (paths in byte order) for each pair of distinct non-test files git does not ignore, of the
# same extension and neither .md, .txt nor .rst, at least one changed in <branch-base>..HEAD, each importing the
# other's module or naming its script by path (#4556); a docstring, comment, identifier or bare string holding the
# other's stem is no reference. The Draft PR step reports them in the PR body (PRD 032.8).
#
# Usage:   coupling.sh <branch-base>
# Exit:    0 one or more pairs printed; 3 no pair; 2 bad arguments or the base does not resolve
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/coupling.py" "$@"

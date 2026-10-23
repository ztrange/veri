#!/bin/sh
# affected-suites.sh — print the suites one change affects, so a red or refactor leaf can run a
# narrow slice of `make test` instead of all of it: a shim over veri/affected_suites.py.
#
# usage: affected-suites.sh <base>..<head>
#
# Prints one suite path per line, sorted, with no duplicate.
# Exit:    0 suites printed; 2 a malformed or unresolvable range; 3 nothing to do
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/affected_suites.py" "$@"

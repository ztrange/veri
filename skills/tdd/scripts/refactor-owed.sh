#!/bin/sh
# refactor-owed.sh — carry a step's structural leftovers out of its refactor loop: a shim over veri/refactor_owed.py.
#
# `append` reads a finished refactor leaf's report on stdin and appends the transform of every
# `CANDIDATES: structural | …` and `CANDIDATES: test-only | …` line to <file> under the named step;
# `applied` and `not-done` record a candidate the pass applied or left undone; `render` prints <file> as the `## Refactor owed` section; `list` prints each structural transform once.
#
# usage:   refactor-owed.sh append <file> '<STEP>' [<bounds>] < leaf-report.txt
#          refactor-owed.sh applied <file> '<transform>' <sha> '<subject>'
#          refactor-owed.sh not-done <file> '<candidate>' <reason>
#          refactor-owed.sh render <file>
#          refactor-owed.sh list <file>
# Exit:    0 done; 1 the append's, applied's or not-done's write failed; 2 a missing argument or an unknown verb;
#          3 render or list found <file> absent or empty, or list found no structural transform
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/refactor_owed.py" "$@"

#!/bin/sh
# refactor-owed.sh — carry a step's structural leftovers out of its refactor loop: a shim over veri/refactor_owed.py.
#
# `append` reads a finished refactor leaf's report on stdin and appends the transform of every
# `CANDIDATES: structural | …` and `CANDIDATES: test-only | …` line to <file> under the named step;
# `render` prints <file> as the `## Refactor owed` section; `list` prints each structural transform once.
#
# usage:   refactor-owed.sh append <file> '<STEP>' [<bounds>] < leaf-report.txt
#          refactor-owed.sh applied <file> '<transform>' <sha>
#          refactor-owed.sh render <file>
#          refactor-owed.sh list <file>
# Exit:    0 done; 1 the append's or applied's write failed; 2 a missing argument or an unknown verb;
#          3 render or list found <file> absent or empty, or list found no structural transform
exec python3 "$(dirname "$0")/veri/refactor_owed.py" "$@"

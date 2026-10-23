#!/bin/sh
# wrong-test-route.sh — decide the leaf that follows a green whose report carries WRONG_TEST: a shim over veri/wrong_test_route.py.
#
# usage: wrong-test-route.sh <green-report> <red-test-id> (prints red <case>, missing <behaviour>, repair <case> <superseded>…, supersede <cases> or revise)
#
# Run from the repository root. Prints `red <case>` (an existing case other than <red-test-id>), `missing <behaviour>`, `repair <case> <superseded>…` (the step's own case), `supersede <case> <case>…` or `revise`.
# Searches Python test files, bash suites and JS/TS test files: *.test.* / *.spec.* over .js .jsx .ts .tsx .mjs .cjs, and files under __tests__/, never .d.ts.
# Reads a WRONG_TEST: name in backticks, double quotes, curly quotes, or as a test_\w+ name.
# Exit:    0 a route other than `revise` printed; 2 bad arguments or an unreadable report — nothing on stdout; 3 `revise` printed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/wrong_test_route.py" "$@"

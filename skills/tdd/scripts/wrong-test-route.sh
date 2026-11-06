#!/bin/sh
# wrong-test-route.sh — decide the leaf that follows a green whose report carries WRONG_TEST: a shim over veri/wrong_test_route.py.
#
# usage: wrong-test-route.sh <green-report> <red-test-id> (prints red <case>, missing <behaviour>, later <step>, repair <case> <superseded>…, supersede <cases> or revise)
#
# Run from the repository root. Prints `red <case>` (an existing case other than <red-test-id> that a CONTRADICTS: line names; a case named only in WRONG_TEST: is evidence and routes to repair), `fixture <path> <name>` (a helper, fixture or shared setup function defined in a test file that is not a test case), `missing <behaviour>`, `later <step>` (an open ledger step after `VERI_STEP` that a `LATER_STEP:` line names, or, with no such line, whose text without its trailing `⟦…⟧` markers contains the `MISSING_TEST:` behaviour or is contained in it, compared case-insensitively), `repair <case> <superseded>…` (the step's own case), `supersede <case> <case>…` or `revise`.
# A fixture route is taken only when the helper is defined in the step's own test file, the one before the double colon in a <file>::<case> id; an id with no double colon (the Go and JS names) falls back to searching every test file.
# Searches Python test files, bash suites and JS/TS test files: *.test.* / *.spec.* over .js .jsx .ts .tsx .mjs .cjs, and files under __tests__/, never .d.ts.
# Reads a WRONG_TEST: name in backticks, double quotes, curly quotes, or as a test_\w+ name.
# Exit:    0 a route other than `revise` printed; 1 `missing-exhausted <behaviour>` printed; 2 bad arguments, an unreadable report, or an unreadable ledger behind a `LATER_STEP:` line — nothing on stdout; 3 `revise` printed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/wrong_test_route.py" "$@"

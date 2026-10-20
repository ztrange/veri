#!/bin/sh
# wrong-test-route.sh — decide the leaf that follows a green whose report carries WRONG_TEST: a shim over veri/wrong_test_route.py.
#
# usage: wrong-test-route.sh <green-report> <red-test-id> (prints red <case>, missing <behaviour>, repair <case>, supersede <cases> or revise)
#
# Run from the repository root. Prints `red <case>` when the WRONG_TEST: line names an existing test case other than <red-test-id>; `revise` otherwise.
# Exit:    0 `red <case>` printed; 2 bad arguments or an unreadable report — nothing on stdout; 3 `revise` printed
exec python3 "$(dirname "$0")/veri/wrong_test_route.py" "$@"

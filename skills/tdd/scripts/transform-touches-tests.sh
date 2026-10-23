#!/bin/sh
# transform-touches-tests.sh — reject a refactor-kind transform whose commits change a test
# file: a shim over veri/transform_touches_tests.py.
#
# The range read is <base-sha>..HEAD, every commit in it. A test file is one under a `tests/`
# directory or named `*.test.*`.
#
# usage: transform-touches-tests.sh <base-sha> [<bound>]
#
# <bound> is a comma-separated file list; given one, a range that changed no test file is
# checked next for files it changed outside the bound.
#
# Exit: 1 naming each test file the range changed, else each file it changed outside
# <bound>; 0 when it changed neither; 2 when
# <base-sha> is missing or resolves to no commit, or the range cannot be read — an unreadable
# range is no answer.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/transform_touches_tests.py" "$@"

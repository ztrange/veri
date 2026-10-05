#!/bin/sh
# transform-touches-tests.sh — reject a refactor-kind transform whose commits change a test
# file: a shim over veri/transform_touches_tests.py.
#
# The range read is <base-sha>..HEAD, every commit in it. A test file is one under a `tests/`
# directory or named `*.test.*`.
#
# usage: transform-touches-tests.sh <base-sha>
#
# Exit: 1 naming each test file the range changed, 0 when it changed none, 2 when
# <base-sha> is missing or resolves to no commit — an unreadable range is no answer.
exec python3 "$(dirname "$0")/veri/transform_touches_tests.py" "$@"

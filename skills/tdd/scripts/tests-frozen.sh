#!/bin/sh
# tests-frozen.sh — record a step's test files, then check that none of them has changed: a shim over veri/tests_frozen.py.
#
# usage: tests-frozen.sh record <record-file> <test-file>...
#        tests-frozen.sh check <record-file>
#
# Exit: 0 recorded, or every recorded file is byte-identical (nothing on stdout),
#       1 with one path per line on stdout for each recorded file edited or deleted,
#       2 bad arguments or an unreadable record/file.
exec python3 "$(dirname "$0")/veri/tests_frozen.py" "$@"

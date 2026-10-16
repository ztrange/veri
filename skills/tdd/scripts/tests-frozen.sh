#!/bin/sh
# tests-frozen.sh — record a step's test files, then check that none of them has changed: a shim over veri/tests_frozen.py.
#
# usage: tests-frozen.sh record <record-file> <test-file>...
#        tests-frozen.sh check <record-file>
#        tests-frozen.sh path <step-text>
#
# path prints the step's record file, .tdd/tests-frozen-<k>.record, where <k> is the first 16 hex
# digits of the SHA-256 of the step text: a step text is often longer than a filename may be and
# may hold a "/", so the text itself is never the filename.
#
# Exit: 0 recorded, the path printed, or every recorded file is byte-identical (nothing on stdout),
#       1 with one path per line on stdout for each recorded file edited or deleted,
#       2 bad arguments (an empty step text included) or an unreadable record/file.
exec python3 "$(dirname "$0")/veri/tests_frozen.py" "$@"

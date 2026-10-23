#!/bin/sh
# production-frozen.sh — reject a range that changes production code while production is
# frozen: a shim over veri/production_frozen.py.
#
# A production file is any changed path transform-touches-tests.sh does not count as a test
# file.
#
# usage: production-frozen.sh <base-sha>
#
# Exit: 1 naming each production file the range <base-sha>..HEAD changed, 2 when <base-sha>
# is missing or does not resolve to a commit.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/production_frozen.py" "$@"

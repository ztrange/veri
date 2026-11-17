#!/bin/sh
# release-covered.sh — put back on the queue the refactor issue a done legacy coverage issue blocked. A shim over veri/release_covered.py.
#
# When issue <n>'s title is `Cover the behaviour #<m> refactors` (the title coverage-blocker.sh files) and #<m> is
# open and labelled `bailed`, releases #<m> as release-issue.sh <m> does and prints `released #<m>`.
#
# Usage: release-covered.sh <issue-number>
# Exit:  0 released | 2 bad arguments, no answer from gh, or release-issue.sh exit 2 | 3 another title shape, #<m> closed or not bailed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/release_covered.py" "$@"

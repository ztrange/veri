#!/bin/sh
# github-outage.sh — the dev session's local mode during a GitHub outage: a shim over veri/github_outage.py.
#
# Usage:   github-outage.sh enter <pr-url> | hold <pr-url> | take --pid <pid> | adopt --pid <pid>
#          github-outage.sh settle <pr-url> merged|failed|released | wait-start | wait-status
#          github-outage.sh wait [<max-seconds>] | status
# Exit:    0 done; 1 enter: GitHub answered and nothing counts; 2 no answer, or bad arguments;
#          3 nothing to do (local mode off, nothing to take or adopt, a wait already live, no wait)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/github_outage.py" "$@"

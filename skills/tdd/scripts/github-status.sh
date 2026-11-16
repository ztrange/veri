#!/bin/sh
# github-status.sh — whether GitHub's status page has an incident on what veri needs: a shim over veri/github_status.py.
#
# Usage:   github-status.sh [<component>…]
# Exit:    0 GitHub answered, nothing counts ("up" or "young" lines); 1 a counting incident, one line each;
#          2 no answer, or a bad argument or tunable
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/github_status.py" "$@"

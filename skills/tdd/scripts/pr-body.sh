#!/bin/sh
# pr-body.sh — write a PR body, keeping every section the run did not author: a shim over veri/pr_body.py.
#
# Usage:   pr-body.sh <pr-number> <body-file>
# Exit:    0 written; 2 bad arguments, or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_body.py" "$@"

#!/bin/sh
# requirements-preflight.sh — checks an issue's requirements rows: a shim over veri/requirements_preflight.py.
#
# usage: requirements-preflight.sh <issue-body-file> [<ledger>]
# Exit:    0 every row is new, identical or <reword>-marked; 2 a clash, a skill-edit unit with no ### heading, or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/requirements_preflight.py" "$@"

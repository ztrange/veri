#!/bin/sh
# branch-suite.sh — settle whether CI stands in for the branch's local full-suite run: a shim over veri/branch_suite.py.
#
# usage: branch-suite.sh
# Exit:    2 bad VERI_BRANCH_SUITE or VERI_CI_ON_PR
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/branch_suite.py" "$@"

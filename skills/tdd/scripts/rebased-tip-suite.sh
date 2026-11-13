#!/bin/sh
# rebased-tip-suite.sh — settle where the rebased tip's full suite runs: a shim over veri/rebased_tip_suite.py.
#
# usage: rebased-tip-suite.sh
# Exit:    2 bad VERI_REBASED_TIP_SUITE or VERI_CI_ON_PR
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/rebased_tip_suite.py" "$@"

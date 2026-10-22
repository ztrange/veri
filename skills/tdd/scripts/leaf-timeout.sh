#!/bin/sh
# leaf-timeout.sh — size the run's hard timeout from the green-baseline run's wall time: a shim over veri/leaf_timeout.py.
#
# Prints the larger of 900 and 6 × the baseline; with refactor, that × max(1, VERI_REFACTOR_BUDGET);
# with --full, derived from <full-seconds>. An explicit VERI_TIMEOUT is printed as given.
#
# usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]
#          VERI_TIMEOUT=<n> leaf-timeout.sh …   # <n> a whole number >= 1, used as given
# Exit:    0 the timeout on stdout; 2 a malformed baseline, full-tier value or VERI_TIMEOUT, nothing on stdout
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/leaf_timeout.py" "$@"

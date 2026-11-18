#!/bin/sh
# seam-settle.sh — after a stage done by hand, write the record its script would have written: a shim over
# veri/seam_settle.py.
#
# Usage:   seam-settle.sh <n> <stage> key=value…
# Exit:    0 the record written; 2 an unknown stage, a missing, unknown, repeated or empty key, a newline (LF or CR)
#          in a value, no open step, no green commit from git, or a missing input
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/seam_settle.py" "$@"

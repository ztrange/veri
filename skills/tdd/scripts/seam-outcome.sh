#!/bin/sh
# seam-outcome.sh — say whether a develop-seam leaf confirmed that a legacy step's seam drives its region: a shim over veri/seam_outcome.py.
#
# Reads a develop-seam leaf's report on stdin. The leaf traced the step's named seam into its named
# region without editing a file; it ends with `SEAM:`, `REACHES: yes|no` and a `PROOF:` line.
#
# usage: seam-outcome.sh (the develop-seam leaf's report on stdin)
#
# stdout:  on REACHES: yes, the seam the SEAM: line names; on REACHES: no, the leaf's reason (its PROOF: line).
# exit:    0 REACHES: yes with a SEAM: line · 1 REACHES: no · 2 no readable REACHES: yes|no line,
#          REACHES: yes with no SEAM: line or SEAM: NONE, or an argument
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/seam_outcome.py" "$@"

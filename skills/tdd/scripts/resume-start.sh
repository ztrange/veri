#!/bin/sh
# resume-start.sh — RESUME.md sub-steps 1-4's fixed calls and the owed verify-plan launch, in one call: a shim over veri/resume_start.py.
#
# Usage:   resume-start.sh <n>
# Exit:    0 every call clean; 3 the verdict-plan wait's slice ran out, so call it again; 2 bad arguments or a missing
#          .tdd/issue-<n>-preflight, ledger or .tdd/issue-<n>-run-start; otherwise the stopping call's own code when
#          neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/resume_start.py" "$@"

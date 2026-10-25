#!/bin/sh
# refactor-triage.sh — decide whether another refactor leaf is worth launching: a shim over veri/refactor_triage.py.
#
# Reads a finished refactor leaf's report on stdin. A candidate line's class is one of six:
# `structural`, `cosmetic`, `test-only`, `out-of-scope`, `in-step` or `out-of-bounds`. Only
# `structural` reaches stdout: the transform of every `CANDIDATES: structural | …` line, one per line.
#
# Usage:   refactor-triage.sh < leaf-report.txt
# Exit:    0 structural candidates printed; 2 a candidate line with no class or an unknown one, or no
#          CANDIDATES: line, a diagnostic on stderr; 3 nothing to do — no structural candidate, or none
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/refactor_triage.py" "$@"

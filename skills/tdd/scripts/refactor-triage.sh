#!/bin/sh
# refactor-triage.sh — decide whether another refactor leaf is worth launching: a shim over veri/refactor_triage.py.
#
# Reads a finished refactor leaf's report on stdin and prints the transform of every
# `CANDIDATES: structural | …` line, one per line.
#
# Usage:   refactor-triage.sh < leaf-report.txt
# Exit:    0 structural candidates printed; 2 a candidate line with no class or an unknown one, or no
#          CANDIDATES: line, a diagnostic on stderr; 3 nothing to do — every candidate cosmetic, or none
exec python3 "$(dirname "$0")/veri/refactor_triage.py" "$@"

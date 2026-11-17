#!/bin/sh
# surround-mutants.sh — run a legacy step's mutant table against its characterization tests: a shim over veri/surround_mutants.py.
#
# Reads every `MUTANT: <file> | <old> | <new>` line of the report files (the develop-surround and
# verify-surround reports) and runs each through `mutation-probe.sh <file> <old> <new> -- <command…>`.
#
# usage: surround-mutants.sh <report-file>… -- <command…>
#
# stdout:  one line per row, `<file> | <old> | <new> <result>`, <result> one of red, survived, no-answer;
#          then `short <k> of <N>` when every row is red but fewer than VERI_SURROUND_MUTANTS (default 5)
# exit:    0 every row red and at least VERI_SURROUND_MUTANTS rows · 1 a row survived, or too few rows ·
#          2 no command, an unreadable report, a malformed MUTANT: line, a row the probe could not answer,
#          or a VERI_SURROUND_MUTANTS that is not a whole number >= 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/surround_mutants.py" "$@"

#!/bin/sh
# clear-refactor-pending.sh — drop the pending mark from one step in the local ledger: a shim over veri/clear_refactor_pending.py.
#
# Strips the mark from the first ticked step that contains <matcher> and carries it, writing a temporary file beside the ledger and renaming it over the ledger.
#
# usage: clear-refactor-pending.sh <ledger-file> <matcher>
# Exit:    0 the mark cleared, the file rewritten;
#          2 a missing argument, the ledger is a directory, does not exist or could not be read, or the cleared
#          ledger could not be written — the file is left untouched; 3 nothing to do — no step matched, the file
#          byte-identical
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/clear_refactor_pending.py" "$@"

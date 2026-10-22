#!/bin/sh
# scope-check.sh — refuse a ledger step that names a new pytest module whose basename is taken: a shim over veri/scope_check.py.
#
# Usage:   scope-check.sh <ledger> <repo-root>
# Exit:    0 every named module is existing or free; 1 a new module's basename exists under tests/py (stderr names both paths); 2 bad arguments
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/scope_check.py" "$@"

#!/bin/sh
# criterion-finished.sh — say whether an issue acceptance criterion is finished: a shim over veri/criterion_finished.py.
#
# usage: criterion-finished.sh <k> < .tdd/issue-<n>.md
#
# A step serves criterion k when it carries `⟦criterion k⟧`.
# Exit:    0 every step serving k done and not refactor-pending; 2 a missing or empty <k>;
#          3 some step serving k open or pending, or no step serving k
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/criterion_finished.py" "$@"

#!/bin/sh
# unreachable.sh — the scripts under skills/tdd/scripts/ that no declared entry point reaches: a shim over veri/unreachable.py.
# Entry points: SKILL.md, the Makefile, the git hooks under docs/hooks/.
#
# usage: unreachable.sh <repo-root>       # one unreachable script per line on stdout;
#                                         # one reached only from tests/ as `test-only: <name>`;
#                                         # a VERI_* knob or script SKILL.md or CLAUDE.md
#                                         # promises and nothing reads as `promised-unread: <name>`
#
# Exit:    0  the list was printed, possibly empty
#          2  no <repo-root>
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/unreachable.py" "$@"

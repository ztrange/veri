#!/bin/sh
# scope-check.sh — refuse a ledger that names a taken pytest module basename, a step with several ⟦criterion k⟧ tags, or a ⟦skill-edit⟧ unit with no ### heading in the spec's ## Requirements (or a ⟦skill-edit⟧ step with no path-shaped unit): a shim over veri/scope_check.py.
#
# Usage:   scope-check.sh <ledger> <repo-root>
# Exit:    0 every named module is existing or free; 1 a new module's basename exists under tests/py (stderr names both paths), or a step carries more than one ⟦criterion k⟧ tag (stderr names the step); 2 bad arguments, a ⟦skill-edit⟧ step's unit has no ### heading under ## Requirements (stderr names the unit), or a ⟦skill-edit⟧ step has no path-shaped backticked token (stderr: no path-shaped unit for skill-edit step: <step>)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/scope_check.py" "$@"

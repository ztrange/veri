#!/bin/sh
# no-product-caller.sh — report each product-file line that still names an old interface: a
# shim over veri/no_product_caller.py.
#
# usage: no-product-caller.sh <name>.sh
#
# Exit: 1 printing file:line for each line that names it, 0 when none does, 2 when <name>.sh
# is missing.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/no_product_caller.py" "$@"

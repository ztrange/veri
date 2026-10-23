#!/bin/sh
# report-cache.sh — the cache /vreport and /vstatus read: a shim over veri/report_cache.py.
#
# Usage:   report-cache.sh refresh
# Exit:    2 no subcommand, or an unknown one
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/report_cache.py" "$@"

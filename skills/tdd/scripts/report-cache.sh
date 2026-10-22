#!/bin/sh
# report-cache.sh — the cache /vreport and /vstatus read: a shim over veri/report_cache.py.
#
# Usage:   report-cache.sh refresh
# Exit:    2 no subcommand, or an unknown one
exec python3 "$(dirname "$0")/veri/report_cache.py" "$@"

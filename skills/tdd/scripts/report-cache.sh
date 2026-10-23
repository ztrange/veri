#!/bin/sh
# report-cache.sh — the cache /vreport and /vstatus read: a shim over veri/report_cache.py.
#
# Usage:   report-cache.sh refresh
# Exit:    2 no subcommand, or an unknown one
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/report_cache.py" "$@"

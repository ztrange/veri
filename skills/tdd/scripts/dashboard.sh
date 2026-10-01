#!/usr/bin/env bash
# dashboard.sh — serve the local web dashboard over this repository's veri runs.
#
# Run from a target repo. Binds 127.0.0.1 only, never another interface: a leaf log holds
# the repo's own code and prompts, so the page must not be reachable from the network.
# The server is stdlib-only python3 — no build step, no npm — and the page it serves is
# the `dashboard.html` sitting beside this script, so a foreign repo gets both through
# the installed symlink.
#
# Usage:   dashboard.sh [port]
#          Serves http://127.0.0.1:<port>/ (default 8765) until interrupted. Ctrl-C
#          (SIGINT) is how it is meant to be stopped, so that is a clean stop and not a
#          failure.
# Exit:    0 served and was interrupted
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"

exec python3 "$HERE/dashboard_endpoints.py" "$HERE/dashboard.html" "${1:-8765}" "$HERE/status.sh" "$HERE/metrics.sh"

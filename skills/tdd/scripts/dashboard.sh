#!/bin/sh
# dashboard.sh — serve the local web dashboard over this repository's veri runs: a shim over veri/dashboard.py.
#
# Run from a target repo. Binds 127.0.0.1 only, never another interface: a leaf log holds
# the repo's own code and prompts, so the page must not be reachable from the network.
# The page it serves is the `dashboard.html` sitting beside this script, so a foreign repo
# gets both through the installed symlink.
#
# usage:   dashboard.sh [port]
#          Serves http://127.0.0.1:<port>/ (default 8765) until interrupted. Ctrl-C
#          (SIGINT) is how it is meant to be stopped, so that is a clean stop and not a
#          failure.
# Exit:    0 served and was interrupted
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/dashboard.py" "$@"

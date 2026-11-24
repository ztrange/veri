#!/bin/sh
# cloud-setup.sh — in a Claude Code cloud session, build veri's environment and put it on the session's PATH: a shim over veri/cloud_setup.py.
#
# Usage:   cloud-setup.sh
# Exit:    0 set up, or not a cloud session; 2 no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/cloud_setup.py" "$@"

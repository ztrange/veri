#!/bin/sh
# cloud-install.sh — add the SessionStart hook that runs cloud-setup.sh in a Claude Code cloud session to a project's .claude/settings.json: a shim over veri/cloud_install.py.
#
# Usage:   cloud-install.sh [repo-root]
# Exit:    0 added or already present; 2 no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/cloud_install.py" "$@"

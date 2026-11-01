#!/bin/sh
# install-links.sh — link veri's operator-typed skills into a project's .claude/skills: a shim over veri/install_links.py.
#
# Usage:   install-links.sh [repo-root]
# Exit:    0 linked; 2 no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/install_links.py" "$@"

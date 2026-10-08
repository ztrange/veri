#!/bin/sh
# wait-leaf.sh — the foreground half of a detached leaf launch: a shim over veri/wait_leaf.py.
#
# Blocks polling for the completion file `.tdd/<name>.exit` the supervisor writes, and exits
# with its code as soon as it lands.
#
# usage: wait-leaf.sh <name> [max-seconds]
#
# Status: whatever the supervisor recorded — 0 success · 1 leaf-failure · 2 killed-stuck —
# 2 a supervisor that exited without recording, or bad arguments; 3 once <max-seconds>
# (default 540) pass with no completion file.
#
# Tunables (env): VERI_POLL poll interval secs (default 1).
exec python3 "$(dirname "$0")/veri/wait_leaf.py" "$@"

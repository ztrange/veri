#!/bin/sh
# detach-command.sh — run a long command in a session of its own, then wait on it: a shim over veri/detach_command.py.
#
# usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]
#
# start  returns 0 at once; the command's output goes to .tdd/<name>.out and its exit code
#        to .tdd/<name>.exit when it ends.
# wait   polls every VERI_POLL seconds (default 1) for at most max-seconds (default 60).
#
# Exit codes (wait):
#   0  the command finished and recorded 0
#   1  the command finished and recorded a non-zero code; that code is printed on stdout
#   2  the command died without recording a code, or bad arguments
#   3  no completion file yet — call again
exec python3 "$(dirname "$0")/veri/detach_command.py" "$@"

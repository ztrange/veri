#!/bin/sh
# profile.sh — say which of a suite's cases are the slow ones, measured rather than guessed: a shim over veri/profile.py.
#
# Sources each suite given into a `bash -c` that sets PS4 and `set -x` itself — bash run as
# uid 0 takes no PS4 from its environment — its trace sent to a file nothing else reads, every
# trace line stamped by PS4 with ${EPOCHREALTIME} (no subprocess, unlike `date +%s.%N`) and
# ${LINENO}. A case ends at each top-level assignment that raises `pass` or `fail` above its
# previous value — the two counters every suite in this tree keeps — so a case's cost is
# the trace time from the previous such boundary (or the suite's first stamp) to its own.
#
# Prints one line `<secs> <suite> case <n> L<a>-<b>` per case whose cost is at or above
# VERI_PROFILE_THRESHOLD (seconds, default 1), slowest first. Exit 0 whether or not any
# case crossed it. Exit 2 when no answer could be obtained: a threshold that is not a
# number of seconds, or a suite whose trace never raises `pass` or `fail`.
#
# Usage:   profile.sh <suite>...
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/profile.py" "$@"

#!/usr/bin/env bash
# tier-usual.sh — what one tier's test-command run usually costs (issue #342, part of
# PRD #335). timed-test-run.sh records a `seconds` per run, but a recorded number is only a
# number until there is something to compare it against. The usual is that something: the
# median of the tier's last 10 `test-run` events.
#
# Usage:   tier-usual.sh <tier>          # prints the median seconds on stdout
#
# The median rather than the mean, because one 400 s outlier — a machine that swapped, a
# first-run executable check — must not move the figure every later run is judged against.
# The last 10 rather than all of them, because a tier's cost changes when the suites do, and
# a run from before that change is not evidence about this one. An even window has no single
# middle, so the answer is the mean of the two: ten runs of 1…10 s are usually 5.5 s, a
# figure neither of which any single run took.
#
# The log is read relative to the directory this runs in, `.tdd/events.jsonl`, the way
# event.sh writes it (event.sh:60) and the way metrics.sh reads it — the issue's worktree.
set -euo pipefail

tier="${1:?usage: tier-usual.sh <tier>}"

log=".tdd/events.jsonl"

# The same apostrophe trap metrics.sh and event.sh carry: this is a single-quoted shell
# string, so a `run's` anywhere inside it ends the program there.
exec python3 -c '
import sys

sys.path.insert(0, sys.argv[3])
from event_log import read_events

tier, path = sys.argv[1], sys.argv[2]

WINDOW = 10

seconds = [float(line["seconds"]) for line in read_events(path)
           if line.get("event") == "test-run" and line.get("tier") == tier]

window = sorted(seconds[-WINDOW:])
middle = len(window) // 2
usual = (window[middle - 1] + window[middle]) / 2 if len(window) % 2 == 0 else window[middle]

print(usual)
' "$tier" "$log" "$(cd "$(dirname "$0")" && pwd)/lib"

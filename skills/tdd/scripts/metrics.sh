#!/usr/bin/env bash
# metrics.sh — what one issue's run cost, read back out of its event log (issue #108, and
# #107/ADR-0014 before it: observability is a per-run event log written by the scripts, not
# a service).
#
# Usage:   metrics.sh <issue-number>
#
# The writers — event.sh for every conductor and supervisor mark, harvest-usage.sh for a
# leaf's closing accounting — leave `.tdd/events.jsonl` behind and nothing reads it. This is
# the reader. One call prints a markdown report on stdout, which the conductor both commits
# beside the ledger and pastes into the issue thread, so the report is a document rather
# than a screenful of text: a table, no colour, nothing that depends on a terminal.
#
# It reports, for now, the four COUNTS of each phase of the run:
#
#   attempts — `launch` events. supervise.sh writes exactly one per leaf it supervises,
#              outside its retry loop (supervise.sh:297), so a launch IS an attempt.
#   PASS / REJECT — `verdict` events, carrying the word verify.sh parsed out of the
#              verifier's answer (verify.sh:239). Only a verifier writes one.
#   kills    — `exit` events whose `status` is `2`: this codebase's no-answer-could-be-
#              obtained code, which supervise.sh reaches for one reason only — the watchdog
#              giving up on a leaf that never answered (supervise.sh:318). Counted apart
#              from the verdicts because a kill is liveness and a verdict is methodology,
#              the same two axes CLAUDE.md keeps exit 1 and exit 2 on.
#
# The row key is the log's own `phase` field, which event.sh writes on every line
# (event.sh:52), so grouping by it invents nothing: a developer leaf and the verifier that
# judged it share a phase, and that is what makes all four counts meaningful in one row. A
# line with no phase — the conductor's own `step-start` and `step-done` marks — is none of
# the three events counted here and raises no row.
#
# The log is read relative to the directory this runs in, `.tdd/events.jsonl`, the way
# event.sh writes it and the way supervise.sh already spells `.tdd/<name>.log` — the issue's
# worktree, in other words, which is where the conductor calls this from.
set -euo pipefail

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
# The number is what the report is ABOUT: it names the file the conductor commits and the
# issue the thread belongs to, so a call that omits it has not said which run it means.
issue="${1:?usage: metrics.sh <issue-number>}"

log=".tdd/events.jsonl"

# Note the apostrophe nobody may write inside the block below: it is a single-quoted shell
# string, so a `run's` in a comment or a docstring ends the program there and python is
# handed the rest as argv. The same trap event.sh and harvest-usage.sh carry.
exec python3 -c '
import json, sys

issue, path = sys.argv[1], sys.argv[2]

# The four counts, in the order the table prints them, each with the column heading it is
# printed under. One list so the headings and the arithmetic cannot come to disagree about
# how many columns there are.
COUNTS = ["attempts", "PASS", "REJECT", "kills"]

# Phase order is the order the phases first appear in the log, which is the order the run
# went through them — red before green before refactor. Sorting the names instead would
# print the run backwards for no reason a reader could act on.
phases = []
counts = {}

def tally(phase, count):
    if phase not in counts:
        phases.append(phase)
        counts[phase] = dict.fromkeys(COUNTS, 0)
    counts[phase][count] += 1

with open(path) as f:
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        line = json.loads(raw)
        phase = line.get("phase", "")
        if not phase:
            continue
        event = line.get("event", "")
        if event == "launch":
            tally(phase, "attempts")
        elif event == "verdict" and line.get("verdict") in ("PASS", "REJECT"):
            tally(phase, line["verdict"])
        elif event == "exit" and line.get("status") == "2":
            tally(phase, "kills")

def row(cells):
    print("| " + " | ".join(cells) + " |")

print("### 📊 Metrics — issue %s" % issue)
print()
row(["phase"] + COUNTS)
row(["---"] + ["---:"] * len(COUNTS))
for phase in phases:
    row([phase] + ["%d" % counts[phase][c] for c in COUNTS])
' "$issue" "$log"

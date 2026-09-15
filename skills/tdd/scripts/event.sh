#!/usr/bin/env bash
# event.sh — append one line to the run's event log (issue #107, ADR-0014: observability is
# a per-run event log written by the scripts, not a service). This is the writer every
# conductor mark goes through, and the first clock in the system.
#
# Usage:   event.sh <event> [key=value …]
#
# One call writes one JSON object to `.tdd/events.jsonl`, relative to the directory it runs
# in — the issue's worktree, the way supervise.sh already spells `.tdd/<name>.log`. The line
# always carries the eight fixed keys `ts`, `issue`, `actor`, `phase`, `step`, `event`,
# `attempt` and `skill_commit`, plus one key per `key=value` argument.
#
# `skill_commit` is the commit of the skill the line was written under (issue #165). A run
# executes whatever is installed at `~/.claude/skills/tdd`, a symlink into a clone that `main`
# moves under a running conductor, so which version a leaf was launched with is a fact only
# the log can carry — and because it is written per line rather than per run, a skill that
# changed mid-flight shows up as the sha changing partway down the file.
#
# `ts` is seconds since the epoch, the unit supervise.sh's `now()` already reads out of
# `date +%s`, so the log and the watchdog measure the same way and a reader subtracts two
# marks without parsing a calendar.
#
# The run context is NOT on the command line: it arrives in the environment as VERI_ISSUE,
# VERI_ACTOR, VERI_PHASE, VERI_STEP, VERI_ATTEMPT and VERI_SKILL_COMMIT, the way SKILL.md's
# preflight already exports VERI_TIMEOUT once for every child of the run. The payload stays
# the caller's to choose; the context stays the run's. A variable that is not set writes its
# key anyway, empty — the eight keys are the line's promise to a reader that groups by phase
# or counts attempts, so "absent" must never be the spelling of "unknown".
#
# The line is composed by python3 (already a dependency here — extract-result.sh execs it)
# rather than by concatenating strings: a payload holds a command with spaces and `=`, or a
# verdict reason a model wrote with quotes and backslashes in it, and an unescaped one would
# make the whole log unparseable. json.dumps is what decides that, not the caller.
set -euo pipefail

# `${1:?msg}` expands $1, but if it is unset or empty it aborts the shell with msg on stderr
# — before the mkdir below, so a mis-called event.sh leaves no trace. `:` is the do-nothing
# builtin: it discards the expanded value, because nothing here needs it. This script's own
# argv already IS python's argv — the event name first, the payload after — so the name is
# not bound to a variable and shifted off only to be spliced back on at the exec.
: "${1:?usage: event.sh <event> [key=value …]}"

mkdir -p .tdd

# The event name and the payload arrive as argv, not interpolated into the program text, so
# nothing in them can be read as python. `partition` splits on the FIRST `=` only, which is
# what leaves `cmd=env VERI_TIMEOUT=1200 …` intact instead of truncated at the second one.
exec python3 -c '
import json, os, sys, time

line = {
    "ts": int(time.time()),
    "issue": os.environ.get("VERI_ISSUE", ""),
    "actor": os.environ.get("VERI_ACTOR", ""),
    "phase": os.environ.get("VERI_PHASE", ""),
    "step": os.environ.get("VERI_STEP", ""),
    "event": sys.argv[1],
    "attempt": os.environ.get("VERI_ATTEMPT", ""),
    "skill_commit": os.environ.get("VERI_SKILL_COMMIT", ""),
}
for arg in sys.argv[2:]:
    key, _, value = arg.partition("=")
    line[key] = value

with open(".tdd/events.jsonl", "a") as f:
    f.write(json.dumps(line) + "\n")
' "$@"

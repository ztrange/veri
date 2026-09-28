#!/usr/bin/env bash
# event.sh — append one line to the run's event log (ADR-0014: observability is
# a per-run event log written by the scripts, not a service). This is the writer every
# conductor mark goes through, and the first clock in the system.
#
# Usage:   event.sh <event> [key=value …]
#
# One call writes one JSON object to `.tdd/events.jsonl`, relative to the directory it runs
# in — the issue's worktree, the way supervise.sh already spells `.tdd/<name>.log`. The line
# always carries the nine fixed keys `ts`, `awake`, `issue`, `actor`, `phase`, `step`,
# `event`, `attempt` and `skill_commit`, plus one key per `key=value` argument.
#
# `skill_commit` is the commit of the skill the line was written under. A run
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
# key anyway, empty — the nine keys are the line's promise to a reader that groups by phase
# or counts attempts, so "absent" must never be the spelling of "unknown".
#
# Perf: this used to `exec python3 -c …` purely to escape and compose the line —
# `json.dumps` was the whole reason python3 was a dependency of a leaf launch at all. A
# supervision calls this three to five times (supervise.sh's launch, an optional retry per
# killed-stuck attempt, and exit; harvest-usage.sh's usage mark on top of that), each paying
# a ~45 ms interpreter start before any work, several hundred times over in a multi-step run.
# The line is now composed in bash: `lib/json-escape.sh`'s `json_escape_string` matches
# `json.dumps(str, ensure_ascii=True)`'s escape table byte for byte (json-escape.test.sh
# proves it against a live python3, not by inspection), and `ts` comes from bash's own
# `printf '%(%s)T'` clock (bash 4.2+) instead of forking
# `date`. The processes this script starts itself are `mkdir -p .tdd` below and
# the awake-clock read: one python3 per event for `time.monotonic()` unless VERI_AWAKE_CLOCK
# names another executable — composing the line still starts none.
#
# No caller in this repo passes a `key=value` argument whose key collides with one of the
# nine fixed keys above, or the same key twice (grepped for both before this was written).
# python's dict would have silently let the later one win; this writes both, as two
# occurrences of the same key — an argument that did either would already be an ambiguous
# line to a reader, and this does not manufacture the ambiguity, only fails to hide it.
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: event.sh <event> [key=value …]" >&2; exit 2; }
event="$1"
shift

mkdir -p .tdd

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/json-escape.sh"

# hazard: printf's %(…)T needs bash 4.2 or newer.
ts=""
printf -v ts '%(%s)T' -1

if [[ -n "${VERI_AWAKE_CLOCK:-}" ]]; then
  awake="$("$VERI_AWAKE_CLOCK")"
else
  awake="$(python3 -c 'import time; print(int(time.monotonic()))')"
fi

declare esc_issue esc_actor esc_phase esc_step esc_event esc_attempt esc_skill_commit
json_escape_string esc_issue        "${VERI_ISSUE:-}"
json_escape_string esc_actor        "${VERI_ACTOR:-}"
json_escape_string esc_phase        "${VERI_PHASE:-}"
json_escape_string esc_step         "${VERI_STEP:-}"
json_escape_string esc_event        "$event"
json_escape_string esc_attempt      "${VERI_ATTEMPT:-}"
json_escape_string esc_skill_commit "${VERI_SKILL_COMMIT:-}"

line="{\"ts\": $ts, \"awake\": $awake, \"issue\": \"$esc_issue\", \"actor\": \"$esc_actor\", \"phase\": \"$esc_phase\", \"step\": \"$esc_step\", \"event\": \"$esc_event\", \"attempt\": \"$esc_attempt\", \"skill_commit\": \"$esc_skill_commit\"}"

for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    key="${arg%%=*}"
    value="${arg#*=}"
  else
    key="$arg"
    value=""
  fi
  declare esc_key esc_value
  json_escape_string esc_key "$key"
  json_escape_string esc_value "$value"
  line="${line%\}}, \"$esc_key\": \"$esc_value\"}"
done

printf '%s\n' "$line" >> .tdd/events.jsonl

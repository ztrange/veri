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
# Perf (issue #290): this used to `exec python3 -c …` purely to escape and compose the line —
# `json.dumps` was the whole reason python3 was a dependency of a leaf launch at all. A
# supervision calls this three to five times (supervise.sh's launch, an optional retry per
# killed-stuck attempt, and exit; harvest-usage.sh's usage mark on top of that), each paying
# a ~45 ms interpreter start before any work, several hundred times over in a multi-step run.
# The line is now composed in bash: `lib/json-escape.sh`'s `json_escape_string` matches
# `json.dumps(str, ensure_ascii=True)`'s escape table byte for byte (json-escape.test.sh
# proves it against a live python3, not by inspection), and `ts` comes from bash's own
# `printf '%(%s)T'` clock (bash 4.2+, required since #320's bash-5 floor) instead of forking
# `date`. The only process this script starts itself is `mkdir -p .tdd` below — unchanged
# from before, and not python3.
#
# No caller in this repo passes a `key=value` argument whose key collides with one of the
# eight fixed keys above, or the same key twice (grepped for both before this was written).
# python's dict would have silently let the later one win; this writes both, as two
# occurrences of the same key — an argument that did either would already be an ambiguous
# line to a reader, and this does not manufacture the ambiguity, only fails to hide it.
set -euo pipefail

# Exit 2, not the 1 a `${1:?…}` expansion aborts with — CLAUDE.md, "Exit codes are the API" (#270).
# The refusal comes before the mkdir below, so a mis-called event.sh leaves no trace.
[[ -n "${1:-}" ]] || { echo "usage: event.sh <event> [key=value …]" >&2; exit 2; }
event="$1"
shift

mkdir -p .tdd

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/json-escape.sh
source "$HERE/lib/json-escape.sh"

# Seconds since the epoch, read by the shell itself: `-1` is this bash builtin's own spelling
# of "now" (strftime under the hood), the way `date +%s` with no `-d`/`-r` already means it.
ts=""
printf -v ts '%(%s)T' -1

# Whole seconds the machine spent awake (#486), from the same clock supervise.sh measures its
# windows on: the executable VERI_AWAKE_CLOCK names, or python's time.monotonic() — which,
# unlike `ts`, does not advance while the machine sleeps, so metrics.sh can subtract the sleep.
if [[ -n "${VERI_AWAKE_CLOCK:-}" ]]; then
  awake="$("$VERI_AWAKE_CLOCK")"
else
  awake="$(python3 -c 'import time; print(int(time.monotonic()))')"
fi

# Each `json_escape_string OUT VALUE` writes into OUT by nameref rather than being captured
# from a `$(...)`: a command substitution still forks a subshell, and this line runs the
# escaper eight-plus times — once per fixed key below, once per payload argument in the loop
# after — so a fork apiece would put back a chunk of exactly the cost issue #290 is cutting.
declare esc_issue esc_actor esc_phase esc_step esc_event esc_attempt esc_skill_commit
json_escape_string esc_issue        "${VERI_ISSUE:-}"
json_escape_string esc_actor        "${VERI_ACTOR:-}"
json_escape_string esc_phase        "${VERI_PHASE:-}"
json_escape_string esc_step         "${VERI_STEP:-}"
json_escape_string esc_event        "$event"
json_escape_string esc_attempt      "${VERI_ATTEMPT:-}"
json_escape_string esc_skill_commit "${VERI_SKILL_COMMIT:-}"

# `ts` alone is written unquoted (a JSON number, matching `int(time.time())` before it); the
# other seven fixed keys are always strings, in the same field order the old python dict
# literal declared them in — `metrics.sh` and the suites read either shape the same way, but
# byte-identity is the goal here, not merely equivalence.
line="{\"ts\": $ts, \"awake\": $awake, \"issue\": \"$esc_issue\", \"actor\": \"$esc_actor\", \"phase\": \"$esc_phase\", \"step\": \"$esc_step\", \"event\": \"$esc_event\", \"attempt\": \"$esc_attempt\", \"skill_commit\": \"$esc_skill_commit\"}"

# The payload, one key=value argument at a time. `partition` splits on the FIRST `=` only
# (python's own rule, kept here) — what leaves `cmd=env VERI_TIMEOUT=1200 …` intact instead
# of truncated at the second one — so both bash patterns below stop at the first `=` too:
# `%%=*` (strip from the first `=` to the end) for the key, `#*=` (strip up to the first `=`)
# for the value. An argument with no `=` at all is the key with an empty value, the same as
# python's `partition` returns for one.
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

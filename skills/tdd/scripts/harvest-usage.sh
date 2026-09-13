#!/usr/bin/env bash
# harvest-usage.sh — turn one finished leaf's closing accounting into a `usage` event
# (issue #107, ADR-0014: observability is a per-run event log written by the scripts, not a
# service).
#
# Usage:   harvest-usage.sh <leaf-name>
#
# The other writers mark what they can see as it happens; this one reads what the leaf
# already wrote down. `claude -p --output-format stream-json` closes every run with a
# `{"type":"result", …}` record carrying the leaf's own accounting — how long it took, how
# much of that was the API, how many turns, how many tokens of each of the four kinds and
# what it cost — and nothing in a run picked those numbers up. One call appends one line to
# `.tdd/events.jsonl`, so a reader has the whole run's cost without opening six .log files.
#
# It takes the NAME, not the log path, for the reason leaf-role.sh's header gives: the name
# is also what the line's actor, phase and attempt are derived from, so a path would make the
# caller spell the leaf twice. `.tdd/<name>.log` is the path supervise.sh already writes that
# name to, relative to the issue's worktree this is run in.
#
# The payload keys are the record's own — `duration_ms`, `duration_api_ms`, `num_turns`,
# `total_cost_usd` and the four `usage.*` counts, unnested. Renaming them would put a
# translation table between the log and the stream that somebody has to keep true; leaving
# them as they arrived means a reader who has seen one has seen the other.
set -euo pipefail

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
name="${1:?usage: harvest-usage.sh <leaf-name>}"

# The one file this program reads, named beside the leaf name it is built from rather than
# spelled at the foot of the python block below, where it arrives as `sys.argv[1]` and says
# nothing about which leaf it belongs to.
log=".tdd/$name.log"

HERE="$(cd "$(dirname "$0")" && pwd)"

# The eight numbers, as the `key=value` arguments event.sh takes, one per line.
#
# The record is found by scanning the WHOLE file for the last `{"type":"result"…}` line, not
# by reading the tail: run-leaf.sh streams the leaf's events and then appends the extracted
# result *text* after them (run-leaf.sh:48-50), so the record is never the last line of the
# log it lives in. Lines that are not JSON objects — that appended text — are skipped, the
# same way extract-result.sh skips them. That scan is a function so the two things this
# program does — find the record, print the numbers out of it — are read one at a time, and
# so the thing the rest of the script talks about has that name in the code too.
#
# Collected into a variable rather than piped, so `set -e` sees python's status: a log with no
# such record (a killed leaf) yields None here and reading its usage raises, so nothing is
# logged, rather than an empty payload being written as if the leaf had reported nothing.
pairs="$(python3 -c '
import json, sys

def closing_result(path):
    """The last {"type":"result", ...} record in the log at path, or None if it holds none."""
    record = None
    for line in open(path):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("type") == "result":
            record = obj           # last result record wins
    return record

record = closing_result(sys.argv[1])
usage = record["usage"]
for key in ("duration_ms", "duration_api_ms", "num_turns", "total_cost_usd"):
    print("%s=%s" % (key, record[key]))
for key in ("input_tokens", "output_tokens",
            "cache_read_input_tokens", "cache_creation_input_tokens"):
    print("%s=%s" % (key, usage[key]))
' "$log")"

# One argument per line, read into an array rather than word-split out of the string: a
# `key=value` is one argument to event.sh whatever is in the value, and splitting on spaces
# would be a promise about these values that this script has no way to keep.
payload=()
while IFS= read -r pair; do
  payload+=("$pair")
done <<< "$pairs"

# The context comes from leaf-role.sh, the same derivation supervise.sh and verify.sh mark
# under, so every event of one leaf files under the same actor, phase and attempt. `$role` is
# deliberately unquoted: it is the `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…` line that script
# prints for `env` to word-split into event.sh's environment.
role="$("$HERE/leaf-role.sh" "$name")"
# shellcheck disable=SC2086  -- intentional word-split of leaf-role.sh's assignments
env $role "$HERE/event.sh" usage "${payload[@]}"

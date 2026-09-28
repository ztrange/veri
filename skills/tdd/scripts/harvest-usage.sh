#!/usr/bin/env bash
# harvest-usage.sh — turn one finished leaf's closing accounting into a `usage` event
# (ADR-0014: observability is a per-run event log written by the scripts, not a
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

[[ -n "${1:-}" ]] || { echo "usage: harvest-usage.sh <leaf-name>" >&2; exit 2; }
name="$1"

log=".tdd/$name.log"

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/leaf-role.sh"

# hazard: the python block is one single-quoted string, so an apostrophe inside it ends it.
# hazard: captured, not piped — a pipeline's status is its last command's, losing python's exit 3.
status=0
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

def usage_pairs(record):
    """The eight numbers in one closing result record, as event.sh key=value arguments."""
    usage = record["usage"]
    pairs = []
    for key in ("duration_ms", "duration_api_ms", "num_turns", "total_cost_usd"):
        pairs.append("%s=%s" % (key, record[key]))
    for key in ("input_tokens", "output_tokens",
                "cache_read_input_tokens", "cache_creation_input_tokens"):
        pairs.append("%s=%s" % (key, usage[key]))
    return pairs

record = closing_result(sys.argv[1])
if record is None:
    sys.exit(3)

for pair in usage_pairs(record):
    print(pair)
' "$log")" || status=$?

case "$status" in
  0) ;;

  3)
    echo "harvest-usage.sh: no closing result record in $log — no usage event appended for $name" >&2
    exit 3
    ;;

  *) exit "$status" ;;
esac

payload=()
while IFS= read -r pair; do
  payload+=("$pair")
done <<< "$pairs"

role="$(leaf_role "$name")"
# hazard: $role is unquoted on purpose, for env to word-split into assignments.
env $role "$HERE/event.sh" usage "${payload[@]}"

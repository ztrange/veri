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
# shellcheck source=lib/leaf-role.sh
source "$HERE/lib/leaf-role.sh"

# The eight numbers, as the `key=value` arguments event.sh takes, one per line.
#
# Each of the two things this program does — find the record, read the numbers out of it — is
# a function, so they are read one at a time and the things the rest of the script talks
# about have those names in the code too. Each keeps the reason it is written the way it is
# next to itself, so a reader meets the rationale at the code it explains rather than three
# screens above it. What is left at the foot is one line composing them, which is the whole
# program said in one place.
#
# Note the apostrophe nobody may write inside this block: it is a single-quoted shell string,
# so a `record's` in a comment or a docstring ends the program there and python is handed the
# rest as argv.
#
# Collected into a variable rather than piped, so this script sees python's status: exit 3 is
# the block's report that the log holds no closing record, which the branch below turns into a
# diagnostic. Piped, that status would be lost and an empty payload written as if the leaf had
# reported nothing.
status=0
pairs="$(python3 -c '
import json, sys

def closing_result(path):
    """The last {"type":"result", ...} record in the log at path, or None if it holds none."""
    # The WHOLE file is scanned rather than its tail read: run-leaf.sh streams the leaf events
    # and then appends the extracted result *text* after them (run-leaf.sh:48-50), so the
    # record is never the last line of the log it lives in. Lines that are not JSON objects —
    # that appended text — are skipped, the same way extract-result.sh skips them.
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
    # Nothing to read, which is not a crash: a killed leaf leaves a log that stops wherever
    # the last write landed. Exit 3 says so in the codes the rest of the suite speaks —
    # nothing to do — and leaves saying it in English to the caller, which knows the leaf
    # name this block was only handed a path to.
    sys.exit(3)

for pair in usage_pairs(record):
    print(pair)
' "$log")" || status=$?

# What the block reported, all three outcomes in one place and in the order of their codes. As
# an `if` for the one interesting code plus a negated test for the rest, the reader had to hold
# "everything that is not 3" in their head across the branch between them to see that 0 was the
# only status that carried on; here the fallthrough is a line of its own.
case "$status" in
  # The eight numbers are in `$pairs`. Everything below this block writes them out.
  0) ;;

  # Absence is not zero: no record means no `usage` line at all, and a line on stderr naming
  # this program and the leaf so a reader of a six-leaf run knows which one went unaccounted
  # for. Exit 3 rather than 0, the code the rest of the scripts use for nothing to do.
  3)
    echo "harvest-usage.sh: no closing result record in $log — no usage event appended for $name" >&2
    exit 3
    ;;

  # Any other non-zero is python failing at something it was expected to do — a record missing
  # one of the eight keys, an unreadable log — and is passed on rather than folded into the
  # arm above, which would report a broken harvester as a killed leaf.
  *) exit "$status" ;;
esac

# One argument per line, read into an array rather than word-split out of the string: a
# `key=value` is one argument to event.sh whatever is in the value, and splitting on spaces
# would be a promise about these values that this script has no way to keep.
payload=()
while IFS= read -r pair; do
  payload+=("$pair")
done <<< "$pairs"

# The context comes from leaf_role (lib/leaf-role.sh), the same derivation supervise.sh and
# verify.sh mark under, so every event of one leaf files under the same actor, phase and
# attempt. `$role` is deliberately unquoted: it is the `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…`
# line that function prints for `env` to word-split into event.sh's environment. No `||` guard
# here, same as before this was inlined: a name leaf_role refuses returns 2 from the `$(...)`
# subshell it runs in, and this script's `set -e` stops it there, before the payload is
# appended — a refusal is not a harvest that quietly filed under nothing.
role="$(leaf_role "$name")"
# shellcheck disable=SC2086  -- intentional word-split of leaf_role's assignments
env $role "$HERE/event.sh" usage "${payload[@]}"

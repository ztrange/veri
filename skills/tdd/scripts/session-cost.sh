#!/usr/bin/env bash
# session-cost.sh — what a day of Claude sessions cost, read from the session transcripts
# (issue #201).
#
# Usage:   session-cost.sh --since <ISO date> [<transcript.jsonl> ...]
#
# Why this reader exists at all: `harvest-usage.sh` picks up the closing accounting of a
# LEAF, so `.tdd/events.jsonl` knows what the leaves cost and nothing else. On 2026-09-14
# veri development cost ~$840 at API rates and 52% of that was spent by sessions no veri
# metric can see — the conductors and the operator's own session. The transcripts under the
# Claude projects tree carry every request of every session, leaf and interactive alike, and
# this script is the reader of those.
#
# With transcripts named on the command line, those files are the day. With none, they are
# DISCOVERED: Claude Code names a project directory after the working directory the session
# was started in, slugged — every `/` a `-` — so this repo's spend is spread over the main
# clone's directory and one per worktree cut under it (`…-veri`, `…-veri--tdd-wt-193`). The
# criterion is the PREFIX, not the exact slug: matching only the latter would report the
# operator's own session and miss every run, which is most of the spend.
#
# The money comes out split three ways rather than as one figure, because the action each
# implies is different: cache READS are context re-read on every request (clear the
# session), cache WRITES are a TTL being re-paid, OUTPUT is work actually done. A single
# total says the day was expensive and nothing about which of the three to go and fix.
set -euo pipefail

since=""
transcripts=()

# The call this script accepts, spelled once: three of the checks below quote it back, and
# three spellings of one synopsis are three chances for the one a reader is shown to be the
# stale one.
USAGE="usage: session-cost.sh --since <ISO date> [<transcript.jsonl> ...]"

# `--since` is required. It has no default here on purpose: a default of "today" is a
# decision about which day a report with no date means, and that is its own step.
while [[ $# -gt 0 ]]; do
  case "$1" in
    --since)
      since="${2:?$USAGE}"
      shift 2
      ;;
    *)
      transcripts+=("$1")
      shift
      ;;
  esac
done

[[ -n "$since" ]] || { echo "$USAGE" >&2; exit 2; }

# Every transcript of every project directory this repo owns. The repo root is resolved
# with `pwd -P` before it is slugged because that is the spelling Claude Code slugged: a
# `/var` that is really `/private/var` names a different directory under either reading.
discover() {
  local root slug projects dir file
  root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "$root" ]] ||
    { echo "session-cost.sh: no transcript named, and not inside a git repository" >&2; exit 2; }
  root="$(cd "$root" && pwd -P)"
  slug="${root//\//-}"
  projects="$HOME/.claude/projects"
  [[ -d "$projects" ]] || return 0
  # The glob is the prefix predicate: `$slug` itself and every directory whose name extends
  # it — a worktree's — and nothing else, so another repo's directory is never summed in.
  for dir in "$projects/$slug"*/; do
    [[ -d "$dir" ]] || continue
    for file in "$dir"*.jsonl; do
      [[ -f "$file" ]] && transcripts+=("$file")
    done
  done
}

[[ "${#transcripts[@]}" -gt 0 ]] || discover

[[ "${#transcripts[@]}" -gt 0 ]] ||
  { echo "session-cost.sh: no transcripts found for this repository" >&2; exit 2; }

for t in "${transcripts[@]}"; do
  [[ -f "$t" ]] || { echo "session-cost.sh: no such transcript: $t" >&2; exit 2; }
done

# Note the apostrophe nobody may write inside the block below: it is a single-quoted shell
# string, so a `record's` in a comment or a docstring ends the program there and python is
# handed the rest as argv. Same trap harvest-usage.sh carries.
python3 -c '
import json, sys
from datetime import datetime

# Public per-million-token rates, keyed by model family. A table rather than four numbers
# spelled into the arithmetic below, so the day the prices move there is one place to
# change and one place to read what they were. Last checked 2026-09-15.
PRICES = {
    "opus": {"input": 15.00, "cache_read": 1.50, "cache_write_5m": 18.75, "output": 75.00},
}

# The four kinds of token a request is billed for: the name this script calls the kind by,
# the `usage` field it is counted from, the PRICES key it is billed at, and the words the
# report names it in. One table rather than the same four kinds listed once to be zeroed,
# once to be summed, once to be priced and once to be printed — four listings that have to
# be kept in step by hand, and the next steps add kinds to them (the 1h cache-write tier).
KINDS = (
    ("cache_read",  "cache_read_input_tokens",     "cache_read",     "cache read"),
    ("cache_write", "cache_creation_input_tokens", "cache_write_5m", "cache write"),
    ("output",      "output_tokens",               "output",         "output"),
    ("input",       "input_tokens",                "input",          "input"),
)

def family(model):
    """The price-table key for a model id like `claude-opus-4-1-20250805`."""
    for key in PRICES:
        if key in model:
            return key
    return None

def local_date(stamp):
    """The LOCAL calendar day of a transcript timestamp like `2026-09-14T12:04:31.807Z`.

    Local rather than UTC because a day is the operator day, and the machine TZ is what
    says where that day starts. The `Z` python*s parser will not take becomes `+00:00`.
    """
    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return moment.astimezone().date().isoformat()

def usage_records(path, since):
    """Every REQUEST in the transcript at path that states a `usage` and falls on or after
    `since`. Lines that are not JSON objects, and records carrying no usage — a `summary`,
    a `user` turn — are skipped, which is what keeps a reader of LINES from counting them.

    A request is not a record: Claude Code writes one line per content block of an
    assistant turn — the thinking, then each tool call — and every one of them repeats the
    SAME `usage`, because all of them account for the one API request that produced the
    turn. Runs of six were observed on the day #201 measured, where summing lines rather
    than requests overstated the bill by ~40%. So `requestId` is the unit, and the second
    record bearing one has already been paid for. A record carrying no id is its own
    request: there is nothing to say it repeats another.
    """
    seen = set()
    for line in open(path):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        usage = obj.get("message", {}).get("usage")
        stamp = obj.get("timestamp")
        if not usage or not stamp:
            continue
        if local_date(stamp) < since:
            continue
        request = obj.get("requestId")
        if request is not None:
            if request in seen:
                continue
            seen.add(request)
        yield obj

def totals(records):
    """The four token counts, and the model families they were billed at, over `records`."""
    tokens = {kind: 0 for kind, _, _, _ in KINDS}
    models = set()
    for obj in records:
        usage = obj["message"]["usage"]
        models.add(obj["message"].get("model", ""))
        for kind, field, _, _ in KINDS:
            tokens[kind] += usage.get(field, 0)
    return tokens, models

since, paths = sys.argv[1], sys.argv[2:]

def every_record():
    """Every priced record of every transcript, so the report is one day and not one file.
    The day is the repo’s, and the repo spends it across as many project directories as it
    has worktrees."""
    for path in paths:
        for obj in usage_records(path, since):
            yield obj

tokens, models = totals(every_record())

# One model family per report at this size, and it is the price table that has to know it:
# a model the table does not list must not be silently billed as one it does.
known = [f for f in (family(m) for m in models) if f]
if not known:
    print("session-cost.sh: no known model in any transcript", file=sys.stderr)
    sys.exit(2)
price = PRICES[known[0]]

cost = {kind: tokens[kind] * price[rate] / 1e6 for kind, _, rate, _ in KINDS}

# The labels are what a reader acts on, so each line names its figure in words and then
# states the tokens it is a price for. The total is every kind, input included: it is the
# bill, not a sum of the three interesting parts of it.
print("since %s  %d transcript(s)" % (since, len(paths)))
for kind, _, _, label in KINDS:
    print("  %-12s %12d tokens   $%.2f" % (label, tokens[kind], cost[kind]))
print("  %-12s %12s           $%.2f" % ("total", "", sum(cost.values())))
' "$since" "${transcripts[@]}"

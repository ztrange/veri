#!/usr/bin/env bash
# session-cost.sh — what a day of Claude sessions cost, read from the session transcripts
# (issue #201).
#
# Usage:   session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]
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
as_json=""
transcripts=()

USAGE="usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --since)
      # hazard: `${2:?}` would abort with status 1, the code reserved for an answer.
      [[ -n "${2:-}" ]] || { echo "$USAGE" >&2; exit 2; }
      since="$2"
      shift 2
      ;;
    --json)
      as_json=1
      shift
      ;;
    *)
      transcripts+=("$1")
      shift
      ;;
  esac
done

[[ -n "$since" ]] || { echo "$USAGE" >&2; exit 2; }

discover() {
  local root slug projects dir file
  root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "$root" ]] ||
    { echo "session-cost.sh: no transcript named, and not inside a git repository" >&2; exit 2; }
  root="$(cd "$root" && pwd -P)"
  slug="${root//\//-}"
  projects="$HOME/.claude/projects"
  [[ -d "$projects" ]] || return 0
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

# hazard: the python block is one single-quoted string, so an apostrophe inside it ends it.
python3 -c '
import json, sys
from datetime import datetime

PRICES = {
    "opus": {
        "input": 15.00,
        "cache_read": 1.50,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "output": 75.00,
    },
}

def cache_write_tokens(usage):
    split = usage.get("cache_creation")
    if split:
        return {
            "cache_write_1h": split.get("ephemeral_1h_input_tokens", 0),
            "cache_write_5m": split.get("ephemeral_5m_input_tokens", 0),
        }
    return {"cache_write_5m": usage.get("cache_creation_input_tokens", 0)}

def one_rate(field, rate):
    """A kind billed at a single rate: whatever `field` says, all of it at `rate`."""
    return lambda usage: {rate: usage.get(field, 0)}

KINDS = (
    ("cache_read",  one_rate("cache_read_input_tokens", "cache_read"), "cache read"),
    ("cache_write", cache_write_tokens,                                "cache write"),
    ("output",      one_rate("output_tokens", "output"),               "output"),
    ("input",       one_rate("input_tokens", "input"),                 "input"),
)

def model_id(obj):
    """The model a record was billed to, or "" for a record that does not say.

    One spelling of the reach into the message, because the three places that ask — which
    records are priceable, which family to price them at, and which unpriceable model owes
    a footer line — must ask the same question. A second spelling that forgot the default
    would raise on the one record the report exists to notice.
    """
    return obj["message"].get("model", "")

BILLED = tuple(kind for kind, _, _ in KINDS)
CONTEXT = tuple(kind for kind in BILLED if kind != "output")

def weigh(usage, kinds):
    """The tokens of one request over `kinds`, read through `KINDS` and summed.

    One spelling for the two questions asked of a single `usage` — what it weighed and
    what it was billed for — because both have to read a cache write the way the money
    does: through `cache_write_tokens`, which is what stops the flat
    `cache_creation_input_tokens` being counted a second time beside the TTL split it is
    the sum of. Two hand-rolled comprehensions would each be one `KINDS` entry away from
    disagreeing with the bill.
    """
    return sum(count
               for kind, read, _ in KINDS if kind in kinds
               for count in read(usage).values())

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
    """Each kind of token counted PER RATE over `records`.

    Per rate rather than per kind because one kind — the cache write — is billed at two,
    and a single figure for it could only be right if they were one price.
    """
    tokens = {kind: {} for kind, _, _ in KINDS}
    for obj in records:
        usage = obj["message"]["usage"]
        for kind, read, _ in KINDS:
            for rate, count in read(usage).items():
                tokens[kind][rate] = tokens[kind].get(rate, 0) + count
    return tokens

def unpriced(records):
    """Tokens billed to a model `PRICES` has no rate for, per model id, in the order met.

    Reported rather than dropped, and reported in tokens rather than in money: the request
    happened and was billed, so leaving it out understates the day as badly as pricing it
    as a family that was never called. There is no honest third option — a $0.00 beside it
    would be this script claiming the tokens were free.
    """
    rows = {}
    for obj in records:
        model = model_id(obj)
        if family(model):
            continue
        rows[model] = rows.get(model, 0) + weigh(obj["message"]["usage"], BILLED)
    return rows

def context(usage):
    """Everything the model was HANDED on one request: its input, what it read from the
    cache and what it wrote to it. Output is not context — it is what came back, and a
    session is not long because it answered at length. Weighed through the same table as
    the money split, so a session row and the day’s totals cannot disagree about what a
    request weighed.
    """
    return weigh(usage, CONTEXT)

RAMP_FACTOR = 1.5

def verdict(requests, preamble, total):
    floor = requests * preamble
    return "un-cleared ramp" if floor and total > floor * RAMP_FACTOR else ""

def sessions(records):
    """Per session, in the order met: how many requests it made, its PREAMBLE (the first
    request’s context, the fixed floor every later request pays again), its FINAL context
    (how far it ran up) and the TOTAL it read.

    Three figures rather than one because none of them answers alone: a total says how
    much without saying whether that was many cheap requests or few enormous ones, and a
    preamble says only how the session started. And the VERDICT those three come to, in
    words, which is the one thing on the row a reader does not have to do arithmetic for.
    """
    rows = {}
    for obj in records:
        weight = context(obj["message"]["usage"])
        row = rows.setdefault(obj.get("sessionId", ""),
                              {"requests": 0, "preamble": weight, "final": 0, "total": 0,
                               "harness": obj.get("entrypoint", "")})
        row["requests"] += 1
        row["final"] = weight
        row["total"] += weight
    return {key: dict(row, verdict=verdict(row["requests"], row["preamble"], row["total"]))
            for key, row in rows.items()}

def harness_label(harness):
    return harness or "conductor"

def bands(rows):
    """Each harness*s preamble population as (min, median, max), in the order met.

    A band rather than one number because one number from a population of sessions is a
    number that might be the outlier: the wrong conclusion this reports exists to prevent
    was drawn by comparing two single baselines, one of which was not the harness it was
    taken for. The median is the middle of the sorted preambles — for an even group, the
    upper of the middle pair, which is a convention and not a measurement.
    """
    groups = {}
    for row in rows.values():
        groups.setdefault(row["harness"], []).append(row["preamble"])
    banded = {}
    for harness, preambles in groups.items():
        preambles.sort()
        banded[harness] = (preambles[0], preambles[len(preambles) // 2], preambles[-1])
    return banded

ROLES = (
    ("sdk-cli", "sdk-cli (leaf)"),
    (None,      "interactive"),
)

def role(obj):
    return "sdk-cli" if obj.get("entrypoint") == "sdk-cli" else None

since, as_json, paths = sys.argv[1], bool(sys.argv[2]), sys.argv[3:]

records = [obj for path in paths for obj in usage_records(path, since)]

priced = [obj for obj in records if family(model_id(obj))]
tokens = totals(priced)

if not priced:
    print("session-cost.sh: no known model in any transcript", file=sys.stderr)
    sys.exit(2)
price = PRICES[family(model_id(priced[0]))]

def costed(tokens):
    """What each kind of token in `tokens` comes to, at `price`."""
    return {
        kind: sum(count * price[rate] for rate, count in tokens[kind].items()) / 1e6
        for kind, _, _ in KINDS
    }

def row(label, tally, amount):
    """One row of the report, and the only place its layout is written.

    A row is a label, what the money is a price FOR, and the money. The split states a
    token count in the middle field; the rows that are a single figure — the day’s total,
    a role’s — leave it blank. Two spellings of this drifted by a space and the report read
    as two tables: the total’s money column sat one character right of the split’s until
    this became the one spelling. The label field is as wide as the widest label the report
    prints, `sdk-cli (leaf)`, for the same reason — a label that overflows its field pushes
    its own money column right.
    """
    print("  %-14s %19s   $%.2f" % (label, tally, amount))

def bill(tokens):
    """What a bundle of tokens comes to in money, every kind of it summed.

    The one arithmetic a row that is a single figure does — the day’s total, a role’s —
    so it is spelled once: two spellings of it are two chances for one of the rows to come
    to be a sum of three kinds while the other is a sum of four.
    """
    return sum(costed(tokens).values())

cost = costed(tokens)

if as_json:
    print(json.dumps({
        "since": since,
        "transcripts": len(paths),
        "cost": dict(cost, total=bill(tokens)),
    }, indent=2))
    sys.exit(0)

counted = {kind: sum(tokens[kind].values()) for kind, _, _ in KINDS}
print("since %s  %d transcript(s)" % (since, len(paths)))
for kind, _, label in KINDS:
    row(label, "%d tokens" % counted[kind], cost[kind])
row("total", "", bill(tokens))
for key, label in ROLES:
    theirs = totals(obj for obj in priced if role(obj) == key)
    row(label, "", bill(theirs))

session_rows = sessions(records)
print("  per session")
for key, session in session_rows.items():
    print("    %s  %s  preamble %d  final %d  read %d  %s"
          % (key, harness_label(session["harness"]), session["preamble"],
             session["final"], session["total"], session["verdict"]))

print("  baselines by harness")
for harness, (low, mid, high) in bands(session_rows).items():
    print("    %-14s min %d  median %d  max %d" % (harness_label(harness), low, mid, high))

strangers = unpriced(records)
if strangers:
    print("  not priced, no rate in the table for:")
    for model, count in strangers.items():
        print("    %s  %d tokens" % (model, count))
' "$since" "$as_json" "${transcripts[@]}"

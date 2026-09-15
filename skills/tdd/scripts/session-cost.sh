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
    "opus": {
        "input": 15.00,
        "cache_read": 1.50,
        # A cache write has two prices, because it has two TTLs: 1.25x base input for
        # the 5m tier, 2x for the 1h one — 1.6x apart. What follows for a record that
        # states only their sum is at `cache_write_tokens`, which is where it is acted on.
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.00,
        "output": 75.00,
    },
}

# How a kind of token is read out of one `usage` object: the answer is not a number but a
# number PER RATE, because a cache write is billed at two. `cache_creation` states the
# split by TTL and is what a write is priced from when it is there; the flat
# `cache_creation_input_tokens` beside it is the sum of the two, so it is only readable
# when the split is absent, and then only at the cheaper of the two rates — guessing 1h
# would invent spend nobody was charged.
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

# The four kinds of token a request is billed for: the name this script calls the kind by,
# how its tokens are read and at which rate(s), and the words the report names it in. One
# table rather than the same four kinds listed once to be zeroed, once to be summed, once
# to be priced and once to be printed — four listings that have to be kept in step by hand.
KINDS = (
    ("cache_read",  one_rate("cache_read_input_tokens", "cache_read"), "cache read"),
    ("cache_write", cache_write_tokens,                                "cache write"),
    ("output",      one_rate("output_tokens", "output"),               "output"),
    ("input",       one_rate("input_tokens", "input"),                 "input"),
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

def families(records):
    """The price-table keys of the models billed in `records`, in the order met.

    Its own pass rather than a second thing `totals` hands back: which prices to use is
    asked once, of the whole day, while the counting is asked again of every role, and a
    caller that wants one of two answers has to say which one it is discarding.
    """
    return [f for f in (family(obj["message"].get("model", "")) for obj in records) if f]

def context(usage):
    """Everything the model was HANDED on one request: its input, what it read from the
    cache and what it wrote to it. Output is not context — it is what came back, and a
    session is not long because it answered at length. Read through the same table as the
    money split, so a session row and the day’s totals cannot disagree about what a
    request weighed: `cache_write_tokens` is what keeps the flat
    `cache_creation_input_tokens` from being counted a second time beside the TTL split it
    is the sum of.
    """
    return sum(count
               for kind, read, _ in KINDS if kind != "output"
               for count in read(usage).values())

# How far past its own floor a session has to have read before the report says the word.
# A session that is cleared re-reads about its preamble each request, so its total lands
# near 1x this product; the one #201 is named for read 3.55x it. Anything between is a
# session someone let run, and 1.5 is the line: far enough above 1.0 that a cleared
# session with a few long turns is not accused, far enough below 3.55 that the pattern the
# issue measured cannot hide under it.
RAMP_FACTOR = 1.5

# Why a session is expensive, in words, on its own row. The arithmetic that answers it —
# total read against request count times preamble — is exactly the arithmetic nobody did
# on the day measured, so leaving it to the reader is leaving it undone.
def verdict(requests, preamble, total):
    floor = requests * preamble
    return "un-cleared ramp" if floor and total > floor * RAMP_FACTOR else ""

def sessions(records):
    """Per session, in the order met: how many requests it made, its PREAMBLE (the first
    request’s context, the fixed floor every later request pays again), its FINAL context
    (how far it ran up) and the TOTAL it read.

    Three figures rather than one because none of them answers alone: a total says how
    much without saying whether that was many cheap requests or few enormous ones, and a
    preamble says only how the session started.
    """
    rows = {}
    for obj in records:
        weight = context(obj["message"]["usage"])
        # One update path, taken by the first request of a session as much as by the
        # tenth: what the row starts as is only what nothing has been counted into yet.
        # Two paths would say what `final` and `total` are twice over, and the first
        # request is the one whose figures a second spelling would get to state alone.
        # The PREAMBLE is the exception and the reason the default is written here: it is
        # the first request*s context and no later one touches it again.
        row = rows.setdefault(obj.get("sessionId", ""),
                              {"requests": 0, "preamble": weight, "final": 0, "total": 0})
        row["requests"] += 1
        row["final"] = weight
        row["total"] += weight
    return rows

# Which of the two ROLES a record belongs to. `entrypoint` is what Claude Code writes to
# say how the session was started, and `sdk-cli` is the one veri launches: `claude -p`,
# i.e. a leaf. Everything else — a terminal, the desktop app — is a human at a keyboard.
# The split is worth a row each because the two are fixed by different acts: a leaf costs
# what its phase costs, an interactive session costs what nobody cleared.
ROLES = (
    ("sdk-cli", "sdk-cli (leaf)"),
    (None,      "interactive"),
)

def role(obj):
    return "sdk-cli" if obj.get("entrypoint") == "sdk-cli" else None

since, paths = sys.argv[1], sys.argv[2:]

def every_record():
    """Every priced record of every transcript, so the report is one day and not one file.
    The day is the repo’s, and the repo spends it across as many project directories as it
    has worktrees."""
    for path in paths:
        for obj in usage_records(path, since):
            yield obj

records = list(every_record())
tokens = totals(records)

# One model family per report at this size, and it is the price table that has to know it:
# a model the table does not list must not be silently billed as one it does.
known = families(records)
if not known:
    print("session-cost.sh: no known model in any transcript", file=sys.stderr)
    sys.exit(2)
price = PRICES[known[0]]

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
counted = {kind: sum(tokens[kind].values()) for kind, _, _ in KINDS}

# The labels are what a reader acts on, so each line names its figure in words and then
# states the tokens it is a price for. A cache write is two rates and one line: what a
# reader does about a write does not depend on its TTL. The total is every kind, input
# included: it is the bill, not a sum of the three interesting parts of it.
print("since %s  %d transcript(s)" % (since, len(paths)))
for kind, _, label in KINDS:
    row(label, "%d tokens" % counted[kind], cost[kind])
row("total", "", bill(tokens))
for key, label in ROLES:
    theirs = totals(obj for obj in records if role(obj) == key)
    row(label, "", bill(theirs))

# And then the same day one session at a time, because the split above says a day was
# expensive without saying which session made it so. The row carries the three context
# figures and, when they say it, the word.
print("  per session")
for key, row in sessions(records).items():
    print("    %s  preamble %d  final %d  read %d  %s"
          % (key, row["preamble"], row["final"], row["total"],
             verdict(row["requests"], row["preamble"], row["total"])))
' "$since" "${transcripts[@]}"

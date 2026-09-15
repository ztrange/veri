#!/usr/bin/env bash
# Unit tests for scripts/session-cost.sh — the cost report read from the session
# transcripts (issue #201). Zero-dependency plain-shell asserts, same idiom as
# harvest-usage.test.sh, which is this suite's nearest neighbour: both are about a
# `usage` record somebody else wrote down.
#
# Why this exists (#201): on 2026-09-14 veri development cost ~$840 at API rates and 52%
# of it was spent by sessions no veri metric can see — the conductors and the operator's
# own session. `harvest-usage.sh` reads the closing record of a LEAF, so `.tdd/events.jsonl`
# knows what the leaves cost and nothing else. The transcripts under the Claude projects
# tree carry every request of every session, leaf and interactive alike, and this script is
# the reader of those.
#
# Contract under test, for this step:
#   session-cost.sh --since <ISO date> <transcript.jsonl>
#     → exit 0, and a report on stdout whose money is split three ways — what the cache
#       READS cost, what the cache WRITES cost, what the OUTPUT cost — and totalled.
#
# The transcript is named on the command line rather than discovered. Discovery is the
# next step's criterion ("every project directory whose slug is prefixed by the repo
# root's slug"), and a suite here may not read a path under the real `~/.claude/projects`
# — nothing in this tree is allowed to depend on what the operator's machine happens to
# hold. Naming the file is what lets this case be about the ARITHMETIC alone: given these
# records, these three figures and their sum.
#
# Why the three figures and not one: the day the issue measured was 51% cache read, 34%
# cache write and 14% output, and the action each number implies is different — reads are
# context re-read on every request (clear the session), writes are the 1h TTL being
# re-paid, output is work actually done. A single total says the day was expensive and
# nothing about which of the three to go and fix. That is why the split is the criterion
# and not a presentation detail.
#
# The prices the expectations below are computed at are the public Opus rates, per million
# tokens: $1.50 cache read, $18.75 cache write at the 5m TTL, $75.00 output, $15.00 input.
# They are the rates the issue's own measurements resolve to — 286.6M reads for $430 is
# $1.50/M, 1.55M output for $117 is $75.00/M — so the fixture and the numbers it is checked
# against have the same provenance as the problem statement.
#
# What this case deliberately does NOT pin, because each is a step of its own:
#   - deduplication by requestId: the two records below carry DIFFERENT ids, so they sum
#     whether or not the script deduplicates. A fixture that shared one id would make this
#     case pass only on an implementation that already did the next-but-one step's work.
#   - the 1h / 5m cache-write split: the fixture writes carry the 5m tier only, and carry
#     it both as the `cache_creation` breakdown and as the `cache_creation_input_tokens`
#     sum that a real record states alongside it. Both readings price to the same $6.15,
#     so this case cannot be passed or failed by how the tiers are told apart.
#   - CLAUDE.md's script and suite counts, which this step also moves:
#     claude-md-counts.test.sh case 1 already holds them to the files on disk, and goes
#     red by itself the moment session-cost.sh and this file land uncounted.
#
# Run: skills/tdd/scripts/tests/session-cost.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SESSION_COST="$HERE/../session-cost.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which of the four figures came out wrong rather than just that one
# did. Same helper, same words, as harvest-usage.test.sh's.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# figure <what> <label-regex> <amount> — complain into `problems` unless the report holds a
# line that names <what> and states <amount> on it. Both halves matter: a report that
# printed the four numbers unlabelled would not have split anything a reader can act on,
# and a report that labelled four wrong numbers would be worse than none.
#
# The label is matched case-insensitively and as an ERE, so the wording of the report is
# the script's business and only the WORDS that identify which figure it is are this
# suite's. The amount is anchored between non-digits, so `1.86` does not match inside
# `11.865`: an assertion that accepted a substring would read a wrong total as the right
# one. A leading `$`, or trailing zeroes, still match — that is spelling, not the number.
figure() {
  local what="$1" label="$2" amount="${3//./\\.}"
  grep -Ei "$label" <<< "$out" | grep -Eq "(^|[^0-9])$amount([^0-9]|$)" ||
    problems+=("$what: want $3 on a line naming it, not found in the report")
}

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# 1. The step's whole criterion: a day's transcript goes in, and what it cost comes out,
#    split three ways and totalled.
#
#    The transcript is two API requests of one session on 2026-09-14 — the day the issue
#    measured — written in the shape Claude Code writes: one JSON object per line, the
#    money in `message.usage`, the model on `message.model`, the moment in `timestamp`.
#    Two requests rather than one because the criterion is a TOTAL, and a script that read
#    the first record and stopped would pass against a single-record fixture.
#
#    Interleaved with them are a `user` line and a `summary` line carrying no usage at
#    all, which is what a real transcript looks like; they exist here so that a reader
#    which counted LINES rather than usage records has something to trip on.
#
#    Every token count is distinct and none is round, so a script that crossed two wires —
#    reads for writes, writes for output — lands on a figure no expectation matches
#    instead of on one that happens to agree.
name="a day's transcript: session-cost.sh totals its cost, split into cache read, cache write and output"
problems=()

transcript="$work/2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4.jsonl"

# The two requests' usage, each number written once here and summed into the expectations
# below in the comment that states the arithmetic. Spelled a second time inside the JSON
# instead, fixture and expectation could drift and the case would go green on a bill the
# transcript never stated.
a_read=800000   ; a_write=200000 ; a_out=15000 ; a_in=3
b_read=440000   ; b_write=128000 ; b_out=8600  ; b_in=1

# What those come to, at the rates in the header:
#   cache read   800000 + 440000 = 1240000 tokens x $1.50/M  = $1.86
#   cache write  200000 + 128000 =  328000 tokens x $18.75/M = $6.15
#   output        15000 +   8600 =   23600 tokens x $75.00/M = $1.77
#   input             3 +      1 =       4 tokens x $15.00/M = $0.00 (six ten-thousandths
#                                   of a cent — below the cent the report prints, which is
#                                   why the total is the three figures above and the case
#                                   need not take a position on whether input is in it)
#   total                                                      $9.78
want_read_cost=1.86
want_write_cost=6.15
want_output_cost=1.77
want_total_cost=9.78

# The heredoc is unquoted so the `$a_*`/`$b_*` above expand into the JSON. Timestamps are
# UTC mid-afternoon, and the run below fixes TZ=UTC, so the local day the record falls on
# is this suite's own answer and not the machine's.
cat > "$transcript" <<TRANSCRIPT
{"type":"summary","summary":"A cost report read from the session transcripts","leafUuid":"0b1f8c22-4a67-4f30-91da-6c2d3e5b7a19"}
{"type":"user","timestamp":"2026-09-14T12:04:28.331Z","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"user","content":"total the day"}}
{"type":"assistant","timestamp":"2026-09-14T12:04:31.807Z","requestId":"req_011CS4kQn7XdF2vHbJ9tLm3p","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$a_in,"cache_creation_input_tokens":$a_write,"cache_creation":{"ephemeral_5m_input_tokens":$a_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$a_read,"output_tokens":$a_out}}}
{"type":"user","timestamp":"2026-09-14T15:37:09.115Z","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"user","content":"and the split"}}
{"type":"assistant","timestamp":"2026-09-14T15:37:12.244Z","requestId":"req_011CS5rB8xWgT6nPqK4vZy7d","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$b_in,"cache_creation_input_tokens":$b_write,"cache_creation":{"ephemeral_5m_input_tokens":$b_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$b_read,"output_tokens":$b_out}}}
TRANSCRIPT

# `--since` names the fixture's own day rather than leaning on the default, which is today:
# a fixture written by hand carries the date it was written for, and a case that only
# passed while today was that date would be a case with a fuse in it.
out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh, got $code")

figure "cache-read cost"  'cache.*read'  "$want_read_cost"
figure "cache-write cost" 'cache.*(write|creat)' "$want_write_cost"
figure "output cost"      'output'       "$want_output_cost"
figure "total cost"       'total'        "$want_total_cost"

# The report itself, once, when anything above went wrong — four "not found" lines say
# nothing about WHAT the script printed, and that is the first thing a reader needs.
[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

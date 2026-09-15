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
# Contract under test, so far:
#   session-cost.sh --since <ISO date> [<transcript.jsonl>]
#     → exit 0, and a report on stdout whose money is split three ways — what the cache
#       READS cost, what the cache WRITES cost, what the OUTPUT cost — and totalled. With
#       a transcript named, that one file is the day; with none, the day is every project
#       directory whose slug is prefixed by the repo root's (case 2).
#
# Case 1 names the transcript on the command line, which is what lets it be about the
# ARITHMETIC alone: given these records, these three figures and their sum. Whichever way
# the files are found, a suite here may not read a path under the real `~/.claude/projects`
# — nothing in this tree is allowed to depend on what the operator's machine happens to
# hold — so case 2 points `HOME` at a projects tree it wrote itself.
#
# Why the three figures and not one: the day the issue measured was 51% cache read, 34%
# cache write and 14% output, and the action each number implies is different — reads are
# context re-read on every request (clear the session), writes are the 1h TTL being
# re-paid, output is work actually done. A single total says the day was expensive and
# nothing about which of the three to go and fix. That is why the split is the criterion
# and not a presentation detail.
#
# The prices the expectations below are computed at are the public Opus rates, per million
# tokens: $1.50 cache read, $18.75 cache write at the 5m TTL, $30.00 at the 1h one,
# $75.00 output, $15.00 input. They are the rates the issue's own measurements resolve
# to — 286.6M reads for $430 is $1.50/M, 1.55M output for $117 is $75.00/M — so the
# fixture and the numbers it is checked against have the same provenance as the problem
# statement.
#
# What this case deliberately does NOT pin, because each is a step of its own:
#   - deduplication by requestId: the two records below carry DIFFERENT ids, so they sum
#     whether or not the script deduplicates. That is case 3's subject, and keeping it out
#     of here is what leaves case 1 about the arithmetic alone.
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

# states <what> <amount> <where> <lines> — complain into `problems` unless one of <lines>
# states <amount>. The predicate both `figure` and `session_figure` are, written once,
# because what is subtle about it is the matching and not the picking of the lines: a `.`
# in the amount is escaped so it cannot stand for any character, and the amount is
# anchored between non-digits, so `1.86` does not match inside `11.865` — an assertion
# that accepted a substring would read a wrong figure as the right one. A leading `$`, or
# trailing zeroes, still match: that is spelling, not the number.
#
# <lines> arrives as an argument rather than down a pipe on purpose. `problems+=` inside a
# pipeline appends to an array in a subshell, which dies with the pipeline — so a probe
# written that way loses every complaint it makes and its case goes green whatever the
# script printed.
states() {
  local what="$1" amount="${2//./\\.}" where="$3" lines="$4"
  grep -Eq "(^|[^0-9])$amount([^0-9]|$)" <<< "$lines" ||
    problems+=("$what: want $2 on a line $where, not found in the report")
}

# figure <what> <label-regex> <amount> — complain into `problems` unless the report holds a
# line that names <what> and states <amount> on it. Both halves matter: a report that
# printed the four numbers unlabelled would not have split anything a reader can act on,
# and a report that labelled four wrong numbers would be worse than none.
#
# The label is matched case-insensitively and as an ERE, so the wording of the report is
# the script's business and only the WORDS that identify which figure it is are this
# suite's.
figure() {
  states "$1" "$3" "naming it" "$(grep -Ei "$2" <<< "$out")"
}

# expect_split — the whole of what a cost case checks about `$out` and `$code`: the script
# exited 0, and the report states the four figures the case computed into `want_*_cost`,
# each on a line naming which it is. Every case here is that same assertion over a
# different fixture, so it is written once — two spellings of it would let one case quietly
# come to check three figures, and a case that checks three is the one worth least.
#
# The report itself is appended, once, when anything came out wrong: four "not found" lines
# say nothing about WHAT the script printed, and that is the first thing a reader of a red
# run needs. The case closes itself with `report` afterwards, since what it has to do in
# between differs — case 2 has a fixture tree to take down.
expect_split() {
  [[ "$code" == 0 ]] ||
    problems+=("want exit 0 from session-cost.sh, got $code")

  figure "cache-read cost"  'cache.*read'  "$want_read_cost"
  figure "cache-write cost" 'cache.*(write|creat)' "$want_write_cost"
  figure "output cost"      'output'       "$want_output_cost"
  figure "total cost"       'total'        "$want_total_cost"

  [[ "${#problems[@]}" -eq 0 ]] ||
    problems+=("the report was: $(printf '%q' "$out")")
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

expect_split

report "$name"


# 2. The repo's spend is not in one project directory. Claude Code names a project
#    directory after the working directory it was started in, slugged — every `/` a `-` —
#    so the main clone has one directory and EVERY worktree cut under it has its own:
#    `…-ztrange-veri`, `…-ztrange-veri--tdd-wt-193`, `…-ztrange-veri--claude-worktrees-x`.
#    A run happens in a worktree, so a reader that matched the repo root's slug exactly
#    would report the operator's own session and miss the runs — most of the spend. The
#    criterion is therefore the PREFIX: every project directory whose slug starts with the
#    repo root's is this repo's, and they are summed into one report.
#
#    The three halves of that, all pinned here because the predicate is what is under test
#    and a predicate needs both answers: the exact slug is in, a longer slug that extends
#    it is in, and an unrelated repo's slug is OUT.
#
#    Hermetic by construction, and it has to be: a suite here may never read a path under
#    the real `~/.claude/projects` — what that tree holds is whatever the operator's machine
#    happened to do. So the case builds its own: `HOME` points at a scratch directory, and
#    the repo root is a throwaway `git init` the script is invoked from, so the slug under
#    test is one this case wrote rather than one it found.
name="project directories: every slug prefixed by the repo root's is summed, an unrelated one is not"
problems=()

# A scratch tree with NO dot in its path — `mktemp -d`'s own default template is `tmp.XXXX`,
# and a dot is exactly the character whose slugging this case has no business taking a
# position on (the real worktree directories turn `.tdd` into `-tdd`). The repo root below
# is spelled with `pwd -P` for the same reason git does: `git worktree list` answers with
# the resolved path, so a `/var` that is really `/private/var` must be slugged as the
# latter or the fixture directory this case creates is not the one the script looks for.
tree="$(mktemp -d "${TMPDIR:-/tmp}/sessioncostXXXXXX")"
root="$tree/repo"
mkdir -p "$root"
root="$(cd "$root" && pwd -P)"
git -C "$root" init -q 2>/dev/null

home="$tree/home"
projects="$home/.claude/projects"

# The slug, by the one rule this case is entitled to assume: every `/` becomes a `-`.
slug="${root//\//-}"

mkdir -p "$projects/$slug" \
         "$projects/$slug--tdd-wt-999" \
         "$projects/-Users-someone-else-anotherrepo"

# Three transcripts, one per directory, each a single request of its own session. The
# numbers are distinct and unround so a script that summed the wrong set of directories
# lands on a figure no expectation matches; the unrelated repo's are an order of magnitude
# larger than both of this repo's together, so including it cannot be mistaken for a
# rounding difference in any of the three figures.
#
#   this repo, main clone   read 600000  write 100000  output 10000  input 2
#   this repo, worktree     read 300000  write  60000  output  5600  input 1
#   another repo           read 900000  write 900000  output 900000  input 900000
#
# What this repo's two come to, at the header's rates:
#   cache read   600000 + 300000 = 900000 tokens x $1.50/M  = $1.35
#   cache write  100000 +  60000 = 160000 tokens x $18.75/M = $3.00
#   output        10000 +   5600 =  15600 tokens x $75.00/M = $1.17
#   input             2 +      1 =      3 tokens x $15.00/M = $0.00 (below the printed cent)
#   total                                                     $5.52
want_read_cost=1.35
want_write_cost=3.00
want_output_cost=1.17
want_total_cost=5.52

cat > "$projects/$slug/8c1d2e4f-7a93-4b05-8e61-2d7f9a0c3b48.jsonl" <<'MAIN'
{"type":"assistant","timestamp":"2026-09-14T09:12:44.512Z","requestId":"req_011CS6aM2pQrX8dTvB1nHk5w","sessionId":"8c1d2e4f-7a93-4b05-8e61-2d7f9a0c3b48","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":2,"cache_creation_input_tokens":100000,"cache_creation":{"ephemeral_5m_input_tokens":100000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":600000,"output_tokens":10000}}}
MAIN

cat > "$projects/$slug--tdd-wt-999/4e90b7c1-35da-4f27-a0b8-6c19d2e84f3a.jsonl" <<'WORKTREE'
{"type":"assistant","timestamp":"2026-09-14T11:48:02.907Z","requestId":"req_011CS7bN3qRsY9eUwC2pJl6x","sessionId":"4e90b7c1-35da-4f27-a0b8-6c19d2e84f3a","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":1,"cache_creation_input_tokens":60000,"cache_creation":{"ephemeral_5m_input_tokens":60000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":300000,"output_tokens":5600}}}
WORKTREE

cat > "$projects/-Users-someone-else-anotherrepo/1a2b3c4d-5e6f-4071-8293-a4b5c6d7e8f9.jsonl" <<'OTHER'
{"type":"assistant","timestamp":"2026-09-14T13:20:55.104Z","requestId":"req_011CS8cP4rStZ0fVxD3qKm7y","sessionId":"1a2b3c4d-5e6f-4071-8293-a4b5c6d7e8f9","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":900000,"cache_creation_input_tokens":900000,"cache_creation":{"ephemeral_5m_input_tokens":900000,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":900000,"output_tokens":900000}}}
OTHER

# No transcript is named on the command line: which files this repo's day is in is the
# script's question now, and the answer is what the case is about. The invocation runs
# from the throwaway repo so the root the script slugs is that one, with `HOME` pointed at
# the scratch projects tree beside it.
out="$(cd "$root" && HOME="$home" TZ=UTC "$SESSION_COST" --since 2026-09-14 2>&1)"
code=$?

expect_split

rm -rf "$tree"
report "$name"

# 3. A request is not a record. Claude Code writes one transcript line per CONTENT BLOCK
#    of an assistant turn — the thinking, then each tool call — and every one of those
#    lines carries the SAME `message.usage` object, because they are all accounting for the
#    one API request that produced the turn. Runs of six were observed in the transcripts
#    the issue measured, and summing lines rather than requests overstated the day by ~40%.
#    So the unit of the bill is the `requestId`, and a record that repeats one has already
#    been paid for.
#
#    The fixture is one six-block turn — six lines, one `requestId`, one identical usage —
#    followed by a second turn of its own single record with a DIFFERENT id. Both halves
#    are the criterion: the repeated id must be counted once, and the distinct one must
#    still be counted, which is what separates deduplicating from reading the first record
#    of the file and stopping.
#
#    Every expectation below is a figure a summing reader cannot land on: at six-fold the
#    cache read is $8.85 against $2.10, the write $18.75 against $3.75, the output $6.15
#    against $1.50 and the total $33.75 against $7.35 — no digits of a right answer sit
#    inside a wrong one, so this case cannot go green on arithmetic that merely rounded.
name="one request, six records: a repeated requestId is counted once, a distinct one still counts"
problems=()

transcript="$work/6b3e02f7-d914-4c85-a27e-8f01c6b45d3a.jsonl"

# The two REQUESTS' usage — not the seven records'. The first is written into six lines
# below, unchanged each time, which is the whole point of the case.
a_read=900000 ; a_write=160000 ; a_out=12400 ; a_in=3
b_read=500000 ; b_write=40000  ; b_out=7600  ; b_in=1

# What the two requests come to, at the rates in the header:
#   cache read   900000 + 500000 = 1400000 tokens x $1.50/M  = $2.10
#   cache write  160000 +  40000 =  200000 tokens x $18.75/M = $3.75
#   output        12400 +   7600 =   20000 tokens x $75.00/M = $1.50
#   input             3 +      1 =       4 tokens x $15.00/M = $0.00 (below the printed cent)
#   total                                                      $7.35
want_read_cost=2.10
want_write_cost=3.75
want_output_cost=1.50
want_total_cost=7.35

# Six records for the first request, written by a loop rather than by hand. What the case
# turns on is that the `requestId` and the `usage` are IDENTICAL on all six: six copied
# lines can drift into six that are not, and the case would then go green on something
# weaker than its own criterion. Only the content block differs — `thinking`, then five
# tool calls, in the order and shape Claude Code writes them — so that is the loop
# variable, and it differs only so the fixture reads like a transcript.
a_usage="{\"input_tokens\":$a_in,\"cache_creation_input_tokens\":$a_write,\"cache_creation\":{\"ephemeral_5m_input_tokens\":$a_write,\"ephemeral_1h_input_tokens\":0},\"cache_read_input_tokens\":$a_read,\"output_tokens\":$a_out}"

: > "$transcript"
for content in \
  '{"type":"thinking","thinking":"work out the plan"}' \
  '{"type":"tool_use","name":"Bash","input":{"command":"ls"}}' \
  '{"type":"tool_use","name":"Bash","input":{"command":"cat a"}}' \
  '{"type":"tool_use","name":"Bash","input":{"command":"cat b"}}' \
  '{"type":"tool_use","name":"Bash","input":{"command":"cat c"}}' \
  '{"type":"tool_use","name":"Bash","input":{"command":"cat d"}}' ; do
  printf '%s\n' "{\"type\":\"assistant\",\"timestamp\":\"2026-09-14T10:02:11.004Z\",\"requestId\":\"req_011CS9dQ5sTuA1gWyE4rLn8z\",\"sessionId\":\"6b3e02f7-d914-4c85-a27e-8f01c6b45d3a\",\"message\":{\"role\":\"assistant\",\"model\":\"claude-opus-4-1-20250805\",\"content\":[$content],\"usage\":$a_usage}}" >> "$transcript"
done

# The second request: its own single record, with a DIFFERENT id, which is what separates
# deduplicating from reading the first record of the file and stopping.
cat >> "$transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T10:09:47.663Z","requestId":"req_011CSAeR6tUvB2hXzF5sMo9a","sessionId":"6b3e02f7-d914-4c85-a27e-8f01c6b45d3a","message":{"role":"assistant","model":"claude-opus-4-1-20250805","content":[{"type":"text","text":"done"}],"usage":{"input_tokens":$b_in,"cache_creation_input_tokens":$b_write,"cache_creation":{"ephemeral_5m_input_tokens":$b_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$b_read,"output_tokens":$b_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

expect_split

report "$name"


# 4. A cache write has two prices, and the record does not always say which. Claude bills a
#    1h-TTL write at 2x base input and a 5m-TTL write at 1.25x, the two rates in the
#    header, and states the split in `usage.cache_creation` as
#    `ephemeral_1h_input_tokens` and `ephemeral_5m_input_tokens`. The flat
#    `cache_creation_input_tokens` beside them is their SUM, and a sum cannot be priced:
#    the two rates are 1.6x apart, so charging the whole of it at either one is wrong by up
#    to 60% of the write. On the day #201 measured, 9.45M of 9.96M writes were 1h, and
#    pricing them all at the 5m rate understated the day by $105 — a figure larger than
#    most of what the report is read for.
#
#    Three requests, and each is one half of the criterion:
#      A  400000 tokens, 1h tier only     x $30.00/M = $12.00
#      B  400000 tokens, 5m tier only     x $18.75/M =  $7.50
#      C  200000 tokens, NO `cache_creation` at all — only the flat field, which is what a
#         record written before the split existed, or by a client that does not report it,
#         looks like. Nothing says which tier it was, so it is billed at the CHEAPER one,
#         5m: a reader that guessed 1h would invent $2.25 of spend nobody was charged.
#                                            x $18.75/M =  $3.75
#
#    A and B are deliberately the SAME SIZE, which is what makes the ratio the case's
#    subject rather than the sizes: any reader that prices the two tiers alike lands on one
#    number for both, and the only way to $23.25 is the documented 1.6x between them. Both
#    also carry the flat `cache_creation_input_tokens` alongside their breakdown, the way a
#    real record does — so a reader that takes the flat field when a breakdown is present
#    prices A at the 5m rate and is caught here, rather than passing because the fixture
#    only offered it one field to read.
#
#    The whole-report figures a tier-blind reader lands on are $18.75 of write and $19.89
#    of total, against $23.25 and $24.39; neither wrong answer has any digits in common
#    with the right one in the places `figure` anchors on.
name="cache-write tiers: 1h and 5m are priced apart, and a bare cache_creation_input_tokens falls back to 5m"
problems=()

transcript="$work/9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5.jsonl"

# The three requests' usage. The write of each is the tier named in the comment above; the
# reads and outputs are along for the ride, distinct and unround, so that a reader which
# crossed a wire between the write kinds and another kind lands on a figure no expectation
# matches.
a_read=200000 ; a_write_1h=400000 ; a_out=4000 ; a_in=1
b_read=100000 ; b_write_5m=400000 ; b_out=2000 ; b_in=1
c_read=60000  ; c_write_flat=200000 ; c_out=2000 ; c_in=1

# What the three come to, at the rates in the header and the two tiers above:
#   cache read   200000 + 100000 + 60000 =  360000 tokens x $1.50/M  =  $0.54
#   cache write  400000 x $30.00/M + (400000 + 200000) x $18.75/M    = $23.25
#   output         4000 +   2000 +  2000 =    8000 tokens x $75.00/M =  $0.60
#   input              1 +      1 +     1 =        3 tokens x $15.00/M = $0.00 (below the
#                                                            cent the report prints)
#   total                                                              $24.39
want_read_cost=0.54
want_write_cost=23.25
want_output_cost=0.60
want_total_cost=24.39

# Unquoted heredoc, so the token counts above expand into the JSON and are written once.
# Note C's usage: `cache_creation_input_tokens` and no `cache_creation` object beside it.
cat > "$transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T08:15:03.221Z","requestId":"req_011CSBfS7uVwC3iYaG6tNp0b","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$a_in,"cache_creation_input_tokens":$a_write_1h,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":$a_write_1h},"cache_read_input_tokens":$a_read,"output_tokens":$a_out}}}
{"type":"assistant","timestamp":"2026-09-14T08:41:19.508Z","requestId":"req_011CSCgT8vWxD4jZbH7uOq1c","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$b_in,"cache_creation_input_tokens":$b_write_5m,"cache_creation":{"ephemeral_5m_input_tokens":$b_write_5m,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$b_read,"output_tokens":$b_out}}}
{"type":"assistant","timestamp":"2026-09-14T09:03:55.740Z","requestId":"req_011CSDhU9wXyE5kAcI8vPr2d","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$c_in,"cache_creation_input_tokens":$c_write_flat,"cache_read_input_tokens":$c_read,"output_tokens":$c_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

expect_split

report "$name"


# 5. `--since` is a WINDOW, not a label. The report is read to answer "what did today
#    cost", and a transcript is not one day: a session's file accumulates every request it
#    ever made, and the long-lived operator session the issue is named for spans days. So a
#    record whose local day falls before the date given is not this report's, and dropping
#    it is the whole of what the flag does.
#
#    Both halves are pinned in one fixture, because a window needs both answers: a reader
#    that let everything through and one that let nothing through would each satisfy half
#    of this case on its own. One request on 2026-09-13 must be gone; one on 2026-09-14
#    must be there, and its figures are what the report states.
#
#    The day is read LOCAL — `TZ=UTC` on the run below fixes which local day each UTC
#    stamp falls on, so the case answers that question itself rather than inheriting the
#    machine's zone. The two stamps sit mid-afternoon on their own days rather than either
#    side of midnight: where exactly a local day starts is its own question, and this case
#    takes no position on it.
#
#    The figures a reader that summed BOTH requests lands on are $1.50 read, $3.75 write,
#    $1.20 output and $6.45 total — no digits in common with the four below in the places
#    `figure` anchors on, so this case cannot go green on a window it never applied.
name="--since: a record before the window is excluded, one inside it is counted"
problems=()

transcript="$work/c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7.jsonl"

# The two requests' usage. `before` is the one that must not reach the arithmetic at all;
# `inside` is the one the expectations below are computed from.
before_read=300000 ; before_write=80000  ; before_out=6800 ; before_in=2
inside_read=700000 ; inside_write=120000 ; inside_out=9200 ; inside_in=2

# What the INSIDE request alone comes to, at the rates in the header:
#   cache read   700000 tokens x $1.50/M  = $1.05
#   cache write  120000 tokens x $18.75/M = $2.25
#   output         9200 tokens x $75.00/M = $0.69
#   input             2 tokens x $15.00/M = $0.00 (below the cent the report prints)
#   total                                   $3.99
want_read_cost=1.05
want_write_cost=2.25
want_output_cost=0.69
want_total_cost=3.99

cat > "$transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-13T16:22:40.118Z","requestId":"req_011CSEiV0xYzF6lBdJ9wQs3e","sessionId":"c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$before_in,"cache_creation_input_tokens":$before_write,"cache_creation":{"ephemeral_5m_input_tokens":$before_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$before_read,"output_tokens":$before_out}}}
{"type":"assistant","timestamp":"2026-09-14T14:07:33.902Z","requestId":"req_011CSFjW1yZaG7mCeK0xRt4f","sessionId":"c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$inside_in,"cache_creation_input_tokens":$inside_write,"cache_creation":{"ephemeral_5m_input_tokens":$inside_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$inside_read,"output_tokens":$inside_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

expect_split

report "$name"


# 6. A day's total says what the day cost and not WHO spent it. The finding #201 exists for
#    is that 52% of the spend was not a leaf at all — the conductors and the operator's own
#    session — and no aggregate could have said so. So the report is attributed: a session
#    gets its own row, and the row says which ROLE it was, because the two are acted on
#    differently. A leaf is launched by veri and its cost is a run's cost; an interactive
#    session is driven by a human and the only thing that brings its cost down is clearing
#    it.
#
#    Role is read from `entrypoint`, which Claude Code writes at the TOP LEVEL of each
#    record — beside `requestId` and `sessionId`, not inside `message`. A `claude -p` leaf
#    writes `sdk-cli`; anything else (`claude-desktop`, `cli`) is a human at a terminal or
#    an app, so anything-but-`sdk-cli` is interactive. That asymmetry is the rule: a role
#    decided by listing the interactive entrypoints would file a new one silently under the
#    leaves, and a leaf's row is the one a run is billed for.
#
#    The two fixture sessions are alike in everything the script prices — same model, same
#    day, same shape, both single-request — and differ in `entrypoint` and in size alone.
#    That is what leaves `entrypoint` as the only thing the split can have been made on: a
#    reader that keyed on the model, the day or the file's directory puts both sessions in
#    one row and fails here.
#
#    Their totals are the case's expectations, and they are distinct and unround: $2.40 for
#    the leaf, $1.56 for the interactive one. A script that printed one row for the day
#    states neither — their sum is $3.96 — so this case cannot go green on an unattributed
#    report that happens to be labelled.
name="roles: an sdk-cli session and an interactive session are attributed to their own rows"
problems=()

leaf_transcript="$work/3f6d9a71-0c58-4e29-b7a3-1d4e8f2c50b6.jsonl"
human_transcript="$work/7a1c4e82-6b30-4d95-8f16-2e9b0a5d3c74.jsonl"

# Each session's one request. At the rates in the header:
#   leaf         read 400000 x $1.50/M = $0.60   write 80000 x $18.75/M = $1.50
#                output  4000 x $75.00/M = $0.30                  total  $2.40
#   interactive  read 200000 x $1.50/M = $0.30   write 40000 x $18.75/M = $0.75
#                output  6800 x $75.00/M = $0.51                  total  $1.56
#   (input is 1 token each, six ten-thousandths of a cent, below the printed cent)
leaf_read=400000  ; leaf_write=80000  ; leaf_out=4000  ; leaf_in=1
human_read=200000 ; human_write=40000 ; human_out=6800 ; human_in=1

want_leaf_cost=2.40
want_human_cost=1.56

cat > "$leaf_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T10:31:07.442Z","requestId":"req_011CSGkX2zAbH8nDfL1ySu5g","sessionId":"3f6d9a71-0c58-4e29-b7a3-1d4e8f2c50b6","entrypoint":"sdk-cli","userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$leaf_in,"cache_creation_input_tokens":$leaf_write,"cache_creation":{"ephemeral_5m_input_tokens":$leaf_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$leaf_read,"output_tokens":$leaf_out}}}
TRANSCRIPT

cat > "$human_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T10:52:26.019Z","requestId":"req_011CSHlY3aBcI9oEgM2zTv6h","sessionId":"7a1c4e82-6b30-4d95-8f16-2e9b0a5d3c74","entrypoint":"claude-desktop","userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$human_in,"cache_creation_input_tokens":$human_write,"cache_creation":{"ephemeral_5m_input_tokens":$human_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$human_read,"output_tokens":$human_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$leaf_transcript" "$human_transcript" 2>&1)"
code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh, got $code")

# The role words are matched as an ERE, case-insensitively, the way `figure` matches the
# split's labels: whether the leaf row is spelled `sdk-cli` or `leaf` is the script's
# business, and only that the row is identifiable AS that role is this suite's.
figure "the sdk-cli session's row"     'sdk-cli|leaf'  "$want_leaf_cost"
figure "the interactive session's row" 'interactive'   "$want_human_cost"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


# 7. A day's total, even split by role, cannot say WHY an interactive session was
#    expensive. The one the issue is named for — `veri-progress-tdd-d2f962/b2061c86`, 357
#    requests over 15 hours, $204, 24% of the day — was not expensive because of what it
#    read: its tool output totals 47k tokens. It was expensive because nobody ever cleared
#    it, so its context ramped 68,597 → 489,316 and every request re-read the whole of it.
#    A session that is long but CLEARED re-reads roughly its preamble each time and costs
#    what it does; the two look alike in a total and are fixed by different acts, so the
#    report has to tell them apart.
#
#    Three figures per session say which it is, and this case pins all three because one
#    alone answers nothing: the PREAMBLE (the first request's context, the fixed floor
#    every request pays), the FINAL context (how far it ran up) and the TOTAL context read
#    (what was actually billed for over the session). A row carrying the total alone cannot
#    be read against anything; carrying the preamble alone says only how it started.
#
#    And the report says so IN WORDS. A reader who has to divide the total by the request
#    count and the preamble to find the uncleared session is a reader who will not — that
#    arithmetic is exactly what nobody did on the day measured. So the naming is the
#    criterion too, and it needs both answers to be a predicate: the ramping session is
#    named, and the flat one is NOT. A script that printed the word on every row would have
#    said nothing.
#
#    The two fixture sessions are alike in everything else the script looks at — same
#    model, same day, no `entrypoint`, so both are interactive — and differ only in the
#    shape of their context:
#
#      ramp  3 requests, contexts  60004 → 180002 → 400002, total 640008
#            (3 x 60004 = 180012 of preamble owed; 3.55x that was read)
#      flat  2 requests, contexts  52001 → 52001,           total 104002
#            (2 x 52001 = 104002 owed; 1.00x that was read — the whole of it is preamble)
#
#    The flat session's ratio is exactly 1.0 and the ramping one's is 3.55, so no threshold
#    a reader might pick between them can put the two on the same side. Every figure is
#    distinct across both sessions and none is round, so a row that printed the wrong one
#    of the three lands on a number no probe matches.
name="per-session rows: preamble, final and total context, and an un-cleared ramp named in words"
problems=()

ramp_transcript="$work/a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5.jsonl"
flat_transcript="$work/5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e.jsonl"

# Each request's context is its input plus what it read from cache plus what it wrote to
# it: the whole of what the model was handed that turn. Written here once per request and
# summed in the comment above, so fixture and expectation cannot drift apart.
ramp_r1_in=4 ; ramp_r1_read=0      ; ramp_r1_write=60000
ramp_r2_in=2 ; ramp_r2_read=60000  ; ramp_r2_write=120000
ramp_r3_in=2 ; ramp_r3_read=180000 ; ramp_r3_write=220000

flat_f1_in=1 ; flat_f1_read=0     ; flat_f1_write=52000
flat_f2_in=1 ; flat_f2_read=52000 ; flat_f2_write=0

want_ramp_preamble=60004 ; want_ramp_final=400002 ; want_ramp_total=640008
want_flat_preamble=52001 ; want_flat_final=52001  ; want_flat_total=104002

cat > "$ramp_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T07:02:18.443Z","requestId":"req_011CSJmZ4bCdJ0pFhN3aUw7i","sessionId":"a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$ramp_r1_in,"cache_creation_input_tokens":$ramp_r1_write,"cache_creation":{"ephemeral_5m_input_tokens":$ramp_r1_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$ramp_r1_read,"output_tokens":900}}}
{"type":"assistant","timestamp":"2026-09-14T09:26:51.207Z","requestId":"req_011CSKnA5cDeK1qGiO4bVx8j","sessionId":"a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$ramp_r2_in,"cache_creation_input_tokens":$ramp_r2_write,"cache_creation":{"ephemeral_5m_input_tokens":$ramp_r2_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$ramp_r2_read,"output_tokens":700}}}
{"type":"assistant","timestamp":"2026-09-14T13:44:05.912Z","requestId":"req_011CSLoB6dEfL2rHjP5cWy9k","sessionId":"a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$ramp_r3_in,"cache_creation_input_tokens":$ramp_r3_write,"cache_creation":{"ephemeral_5m_input_tokens":$ramp_r3_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$ramp_r3_read,"output_tokens":800}}}
TRANSCRIPT

cat > "$flat_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T08:11:32.605Z","requestId":"req_011CSMpC7eFgM3sIkQ6dXz0l","sessionId":"5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$flat_f1_in,"cache_creation_input_tokens":$flat_f1_write,"cache_creation":{"ephemeral_5m_input_tokens":$flat_f1_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$flat_f1_read,"output_tokens":600}}}
{"type":"assistant","timestamp":"2026-09-14T08:39:14.881Z","requestId":"req_011CSNqD8fGhN4tJlR7eYa1m","sessionId":"5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$flat_f2_in,"cache_creation_input_tokens":$flat_f2_write,"cache_creation":{"ephemeral_5m_input_tokens":$flat_f2_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$flat_f2_read,"output_tokens":500}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$ramp_transcript" "$flat_transcript" 2>&1)"
code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh, got $code")

# A session's lines are the ones naming it. The id is matched on its first eight
# characters, which is how the issue itself writes a session down and is a prefix of the
# full uuid either way: whether the row prints the whole id or an abbreviation of it is the
# script's business, not this suite's. Everything a session's row says is looked for among
# those lines rather than on one line, so the report may lay a session out over as many
# lines as it likes.
session_figure() {
  states "$1" "$3" "naming session $2" "$(grep -F "$2" <<< "$out")"
}

session_figure "the ramping session's preamble"      a8f3d1c6 "$want_ramp_preamble"
session_figure "the ramping session's final context" a8f3d1c6 "$want_ramp_final"
session_figure "the ramping session's context read"  a8f3d1c6 "$want_ramp_total"

session_figure "the flat session's preamble"         5c72e0b4 "$want_flat_preamble"
session_figure "the flat session's final context"    5c72e0b4 "$want_flat_final"
session_figure "the flat session's context read"     5c72e0b4 "$want_flat_total"

# And the verdict, in words, on the session that earned it and not on the one that did not.
# Matched as a case-insensitive ERE over the wordings that would tell a reader what the
# session did — which of them the report picks is the script's business; that it says
# something rather than leaving the division to be done by hand is the criterion.
ramp_words='un-?cleared|never cleared|not cleared|ramp'

grep -F a8f3d1c6 <<< "$out" | grep -Eqi "$ramp_words" ||
  problems+=("the ramping session: want its row to name it as un-cleared in words, matching /$ramp_words/, not found")

! grep -F 5c72e0b4 <<< "$out" | grep -Eqi "$ramp_words" ||
  problems+=("the flat session: its context read is exactly its preamble x its requests, so it must NOT be named as un-cleared, but a line naming it matches /$ramp_words/")

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

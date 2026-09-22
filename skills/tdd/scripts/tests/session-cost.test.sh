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

# anchored <amount> — that predicate as an ERE on its own, for a probe that needs the
# match without the complaint `states` makes: `band` chains three of them to pick a line
# stating all three of a group's figures. One spelling of the pattern, so the escaping and
# the fencing cannot come to differ between the probe that asserts one figure and the one
# that asserts three.
anchored() {
  printf '(^|[^0-9])%s([^0-9]|$)' "${1//./\\.}"
}

states() {
  local what="$1" where="$3" lines="$4"
  grep -Eq "$(anchored "$2")" <<< "$lines" ||
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

grep -Eqi "$ramp_words" < <(grep -F a8f3d1c6 <<< "$out") ||
  problems+=("the ramping session: want its row to name it as un-cleared in words, matching /$ramp_words/, not found")

! grep -Eqi "$ramp_words" < <(grep -F 5c72e0b4 <<< "$out") ||
  problems+=("the flat session: its context read is exactly its preamble x its requests, so it must NOT be named as un-cleared, but a line naming it matches /$ramp_words/")

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


# 8. A price table that does not know a model must not guess. Every figure in this report
#    is a token count multiplied by a rate, and the rate comes from `PRICES`, keyed by
#    model family. A model the table has never heard of — the next one Anthropic ships, a
#    third-party endpoint, a renamed family — has no rate, and there are only two things to
#    do with it: invent one, or say so. Inventing one is the failure that cannot be seen
#    afterwards: the report still prints four tidy figures, the total still looks like
#    money, and nothing on the page says that part of it was priced as a model that was
#    never called. The day #201 measured was reconstructed by hand precisely because no
#    number anywhere could be trusted to mean what it said; a silently mispriced family
#    would put the new report in the same position.
#
#    So the criterion has three clauses and this case pins all three, because any two
#    without the third is still a report that misleads:
#      - the unknown model's TOKENS are reported — it was called, it was billed, and a
#        report that dropped it would understate the day as badly as mispricing it;
#      - its COST is left blank — not $0.00, which is a claim that it was free, but
#        nothing, which is the truth: this script cannot say;
#      - and it is NAMED in a footer, so the reader knows which model to go and price.
#
#    The fixture is one known session and one unknown one, rather than an unknown one
#    alone, because the thing most likely to go wrong is not the footer but the
#    arithmetic: a script that picks one family for the whole report and prices every
#    record at it produces a total that is off by whatever the unknown model spent, and an
#    unknown-only fixture could never catch that — there would be no known rate for it to
#    be wrong about. Here the four money figures are the KNOWN session's alone: $0.90
#    read, $0.75 write, $0.33 output, $1.98 total. If the unknown model's tokens are billed
#    at the opus rates beside it, every one of the four moves.
#
#    The unknown session's `input_tokens` is 0, which no real record states, and it is 0 on
#    purpose: the footer's token figure is then the same number whether the script counts
#    the three kinds this report splits or all four it bills. Whether input belongs in a
#    footer total is a question this case has no business answering, so the fixture is
#    written so that it does not have to.
name="an unknown model: its tokens are reported, its cost is blank, and it is named in a footer"
problems=()

known_transcript="$work/1d8b6f40-2a93-4c17-8e65-3b07d9a4f2e1.jsonl"
unknown_transcript="$work/9e4a2c58-7f61-4b0d-a392-5c81e6b70d43.jsonl"

# The known session's one request, at the rates in the header:
#   cache read   600000 x $1.50/M  = $0.90
#   cache write   40000 x $18.75/M = $0.75
#   output         4400 x $75.00/M = $0.33
#   input             2 x $15.00/M = $0.00 (three hundred-thousandths of a cent)
#   total                            $1.98
known_read=600000 ; known_write=40000 ; known_out=4400 ; known_in=2

want_read_cost=0.90
want_write_cost=0.75
want_output_cost=0.33
want_total_cost=1.98

# The unknown session's one request. Its numbers are deliberately unlike the known
# session's in every digit, so a figure that included them lands nowhere near one an
# expectation above states: priced as opus, the four figures would read $1.67, $1.21,
# $0.56 and $3.44 instead.
unknown_model=claude-quasar-9-20260901
unknown_read=512345 ; unknown_write=24680 ; unknown_out=3107 ; unknown_in=0
want_unknown_tokens=540132   # 512345 + 24680 + 3107, and the input is 0

cat > "$known_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T09:12:44.518Z","requestId":"req_011CSJmZ4bCdJ0pFhN3aUw7i","sessionId":"1d8b6f40-2a93-4c17-8e65-3b07d9a4f2e1","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$known_in,"cache_creation_input_tokens":$known_write,"cache_creation":{"ephemeral_5m_input_tokens":$known_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$known_read,"output_tokens":$known_out}}}
TRANSCRIPT

cat > "$unknown_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T09:48:02.907Z","requestId":"req_011CSKnA5cDeK1qGiO4bVx8j","sessionId":"9e4a2c58-7f61-4b0d-a392-5c81e6b70d43","message":{"role":"assistant","model":"$unknown_model","usage":{"input_tokens":$unknown_in,"cache_creation_input_tokens":$unknown_write,"cache_creation":{"ephemeral_5m_input_tokens":$unknown_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$unknown_read,"output_tokens":$unknown_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$known_transcript" "$unknown_transcript" 2>&1)"
code=$?

# The footer first, and the money after, only because `expect_split` closes by appending
# the report itself when anything has gone wrong: probing the footer ahead of it is what
# puts that dump at the END of the complaints rather than in the middle of them, and makes
# it appear for a footer-only failure too — which is the failure where seeing what the
# script actually printed matters most.
#
# The footer is the line that names the model, states its tokens, and states no money.
# Picked out by the model id because that is the one thing about the footer this suite is
# entitled to fix — the wording around it is the script's business.
footer="$(grep -F "$unknown_model" <<< "$out")"

[[ -n "$footer" ]] ||
  problems+=("the unknown model: want a line naming $unknown_model, the report names it nowhere")

states "the unknown model's tokens" "$want_unknown_tokens" "naming $unknown_model" "$footer"

# Blank, not zero: a `$0.00` beside the model would be this script claiming the tokens were
# free, which is a different and worse answer than declining to price them.
! grep -Eq '\$[0-9]' <<< "$footer" ||
  problems+=("the unknown model: want no money on the line naming it, got $(printf '%q' "$footer")")

# And the four money figures are the KNOWN session's alone — the same assertion every cost
# case here makes, which is what makes "the unknown model was not priced" a statement about
# the whole report rather than about one line of it.
expect_split

report "$name"


# 9. The report has two readers, and only one of them is a person. `--json` exists so that
#    a second thing — a dashboard, a weekly roll-up, the next script — can have the day's
#    figures without parsing a layout that was designed to be read by eye. That is only
#    worth having if the two agree: a machine output that states its own arithmetic is two
#    reports of one day, and the day someone reconciles them by hand is the day both
#    become suspect. So the criterion is not that `--json` emits JSON; it is that what it
#    emits carries the SAME totals the text report prints.
#
#    Which is why this case runs the script TWICE over one fixture — once plain, once with
#    `--json` — and holds both to the same four numbers. The text run goes through
#    `expect_split`, the same assertion every cost case here makes, so "the same totals as
#    the text report" is anchored to a text report this case has itself checked rather than
#    to a comment. A case that only parsed the JSON and trusted it would pass against two
#    reports that disagreed.
#
#    What it does NOT pin is the SHAPE of that JSON — which keys, nested how deep, in what
#    order. That is the script's business, and a suite that fixed it would make every later
#    rearrangement of the document a test failure about nothing. The probe flattens the
#    document to one numeric leaf per line and asks only that a key whose NAME says which
#    figure it is carries the figure: the same standard the text probes hold a label to.
name="--json: the machine output states the same four totals as the text report"
problems=()

json_transcript="$work/6b19d4e7-3c05-42af-9d71-8e260a5fb3c7.jsonl"

# Two requests of one session, numbers unlike every other fixture here, and none of them
# round, so a figure assembled from the wrong records lands nowhere an expectation states.
# At the rates in the header:
#   cache read   700000 + 340000 = 1040000 tokens x $1.50/M  = $1.56
#   cache write  160000 +  96000 =  256000 tokens x $18.75/M = $4.80
#   output        12000 +   7600 =   19600 tokens x $75.00/M = $1.47
#   input             3 +      1 =       4 tokens x $15.00/M = $0.00 (below the cent)
#   total                                                      $7.83
j_a_read=700000 ; j_a_write=160000 ; j_a_out=12000 ; j_a_in=3
j_b_read=340000 ; j_b_write=96000  ; j_b_out=7600  ; j_b_in=1

want_read_cost=1.56
want_write_cost=4.80
want_output_cost=1.47
want_total_cost=7.83

cat > "$json_transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T10:21:07.412Z","requestId":"req_011CSPrE9gHiO5uKmS8fZb2n","sessionId":"6b19d4e7-3c05-42af-9d71-8e260a5fb3c7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$j_a_in,"cache_creation_input_tokens":$j_a_write,"cache_creation":{"ephemeral_5m_input_tokens":$j_a_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$j_a_read,"output_tokens":$j_a_out}}}
{"type":"assistant","timestamp":"2026-09-14T11:58:33.276Z","requestId":"req_011CSQsF0hIjP6vLnT9gAc3o","sessionId":"6b19d4e7-3c05-42af-9d71-8e260a5fb3c7","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$j_b_in,"cache_creation_input_tokens":$j_b_write,"cache_creation":{"ephemeral_5m_input_tokens":$j_b_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$j_b_read,"output_tokens":$j_b_out}}}
TRANSCRIPT

# The text run first: the numbers the JSON is held to are the ones this report is checked
# to state, so it is checked before anything is compared against it.
out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$json_transcript" 2>&1)"
code=$?

expect_split

# And the same day again, asked for machine output. Stderr is kept OFF stdout here, unlike
# every other case: a document is either the whole of what came out or it is not JSON, so
# a warning folded into it would fail the parse for a reason that is not the criterion.
json_err="$work/json.err"
out_json="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 --json "$json_transcript" 2>"$json_err")"
json_code=$?

[[ "$json_code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh --json, got $json_code; stderr was: $(printf '%q' "$(cat "$json_err")")")

# One line per numeric leaf of the document — `<dotted path> <amount to the cent>` — so
# the probe below can ask about a key by name without this suite knowing how the document
# is nested. Money is compared at the cent because that is the precision the text report
# prints: holding the JSON to more would be holding the two to different questions.
flat="$(python3 -c '
import json, sys

def walk(node, path):
    if isinstance(node, dict):
        for key, value in node.items():
            walk(value, (path + "." + str(key)) if path else str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            walk(value, "%s[%d]" % (path, index))
    elif isinstance(node, bool):
        pass
    elif isinstance(node, (int, float)):
        print("%s %.2f" % (path, node))

walk(json.load(sys.stdin), "")
' <<< "$out_json" 2>&1)"
parse=$?

[[ "$parse" == 0 ]] ||
  problems+=("--json: want stdout to parse as one JSON document, it does not: $(printf '%q' "$flat")")

# json_figure <what> <key-regex> <amount> — complain unless the flattened document holds a
# numeric leaf whose path names <what> and whose value is <amount>. Both halves, for the
# reason `figure` checks both: four unlabelled numbers are not a report a second program
# can read, and four labelled wrong ones are worse than none.
#
# `figure`, `session_figure` and this one are the same probe over different lines, so all
# three are `states` with the lines picked differently — which is what makes "the same
# standard the text probes hold a label to", above, a fact about the code rather than a
# claim in a comment. The amount goes through `printf` because the flattened document
# states a leaf to the cent and a `want_*_cost` need not be spelled that way.
json_figure() {
  states "$1" "$(printf '%.2f' "$3")" "naming it in the --json output" "$(grep -Ei "$2" <<< "$flat")"
}

json_figure "the JSON cache-read total"  'cache.*read'          "$want_read_cost"
json_figure "the JSON cache-write total" 'cache.*(write|creat)' "$want_write_cost"
json_figure "the JSON output total"      'output'               "$want_output_cost"
json_figure "the JSON total"             'total'                "$want_total_cost"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the --json output was: $(printf '%q' "$out_json")")

report "$name"


# 10. A baseline is only comparable against another session of the SAME harness. The
#     preamble a session pays on every request is fixed by what opened it — the desktop app
#     carries a wider one than a terminal, a leaf a narrower one than either — and the
#     transcript says which through `entrypoint` alone: nothing else on the record
#     distinguishes a conductor from a terminal session sitting in the same project
#     directory, 350 tokens apart.
#
#     This exists because the omission already cost a wrong conclusion. On 2026-09-15 a
#     CLI session's 53,786-token baseline was compared against 51,986 from what was taken
#     to be a desktop session. It was a conductor. The conclusion drawn — that moving off
#     the desktop app saves nothing — was the reverse of the truth, which is 15,749 tokens
#     a request. So the criterion has two halves and this case pins both:
#       - every session row NAMES the entrypoint that opened it, so the reader of any one
#         row knows what its preamble is a baseline for;
#       - and the report GROUPS the baselines by harness, giving each group as min /
#         median / max, so a population reads as a band rather than as one number that
#         might be the outlier the wrong conclusion was drawn from.
#
#     The fixture is six single-request sessions, three per harness, and the preambles are
#     the figures the issue measured on 2026-09-14 → 15:
#
#       claude-desktop  68597  69535  70436   → min 68597  median 69535  max 70436
#       sdk-cli         28321  31000  33155   → min 28321  median 31000  max 33155
#
#     Three per group and not two, so the median is a question with one answer: for an
#     even-sized group it would depend on whether the script averages the middle pair or
#     takes the lower, which is a convention this suite has no business fixing. And two
#     groups rather than one, because the whole criterion is the SPLIT: pooled, the six
#     preambles band as 28321 / 50876 / 70436, so a report that ignored `entrypoint` and
#     banded the day as one population states neither group's median nor the desktop
#     group's min.
#
#     Each session's preamble is its one request's context — input plus cache read plus
#     cache write — and every one of the six is distinct, so a band assembled from the
#     wrong sessions lands on a number no probe here states.
#
#     The band is looked for on a line that names the harness and carries all THREE of its
#     figures, which is what stops the per-session rows from answering for it: after the
#     first half of this criterion those rows name the harness too, and each carries its
#     own preamble — but no session row can carry all three of a group's, so a report that
#     printed the rows and no band fails here rather than passing on them.
name="harness baselines: every session row names its entrypoint, and the bands are min / median / max per harness"
problems=()

# <session id 8-char prefix> <entrypoint> <input> <cache write> <preamble = their sum>.
# The read is 0 on every one of them: a preamble is a first request, and a first request
# has nothing in the cache to read yet — which is also what makes the three figures on the
# row the same number, so the band cannot be confused with a session that ran on.
desktop_ids=(b2061c86-0d47-4e9a-8153-6fa2c70e91db
             c93172d5-1e58-4f0b-9264-7ab3d81fa2ec
             da4283e6-2f69-40c1-a375-8bc4e92b03fd)
desktop_ins=(597 535 436)
desktop_writes=(68000 69000 70000)
want_desktop_preambles=(68597 69535 70436)

leaf_ids=(eb5394f7-3a70-41d2-b486-9cd5fa3c14ae
          fc64a508-4b81-42e3-c597-ade60b4d25bf
          0d75b619-5c92-43f4-d6a8-bef71c5e36c0)
leaf_ins=(321 1000 155)
leaf_writes=(28000 30000 33000)
want_leaf_preambles=(28321 31000 33155)

# Each group's preambles are listed ascending, which makes the array the band the report
# owes for it: first is the min, middle the median, last the max. One listing of the three
# numbers per group rather than a second copy under a band-shaped name — two copies of a
# figure the case is about are two things to keep in step, and the stale one would be
# asserted against a fixture that no longer produces it.

# One transcript per session, the way Claude Code writes them, each holding the session's
# single request. Written from the tables above rather than spelled out six times: what
# this case is about is which of six preambles lands in which band, and six near-identical
# literals are six chances for a digit to be the thing under test by accident.
transcripts=()
write_session() {
  local id="$1" entrypoint="$2" input="$3" write="$4" stamp="$5" out_tokens="$6"
  local path="$work/$id.jsonl"
  cat > "$path" <<TRANSCRIPT
{"type":"assistant","timestamp":"$stamp","requestId":"req_$id","sessionId":"$id","entrypoint":"$entrypoint","userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$input,"cache_creation_input_tokens":$write,"cache_creation":{"ephemeral_5m_input_tokens":$write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":0,"output_tokens":$out_tokens}}}
TRANSCRIPT
  transcripts+=("$path")
}

for i in 0 1 2; do
  write_session "${desktop_ids[$i]}" claude-desktop "${desktop_ins[$i]}" "${desktop_writes[$i]}" \
    "2026-09-14T1$i:04:31.807Z" "$((1100 + i))"
  write_session "${leaf_ids[$i]}" sdk-cli "${leaf_ins[$i]}" "${leaf_writes[$i]}" \
    "2026-09-14T1$i:37:12.204Z" "$((2200 + i))"
done

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "${transcripts[@]}" 2>&1)"
code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh, got $code")

# First half: the row is identified by the session id, as case 7 identifies one, and has
# to name the harness that opened it. `claude-desktop` and `sdk-cli` share no substring,
# so a fixed-string match on either cannot be answered by the other.
for i in 0 1 2; do
  grep -Fq claude-desktop < <(grep -F "${desktop_ids[$i]:0:8}" <<< "$out") ||
    problems+=("session ${desktop_ids[$i]:0:8}: want its row to name the entrypoint claude-desktop, it does not")
  grep -Fq sdk-cli < <(grep -F "${leaf_ids[$i]:0:8}" <<< "$out") ||
    problems+=("session ${leaf_ids[$i]:0:8}: want its row to name the entrypoint sdk-cli, it does not")
done

# Second half: the band, matched through the suite's own `anchored`: chaining three of
# them picks a line stating all three figures and not one stating 68597 inside 686597.
#
# band <harness> <min> <median> <max> — complain unless one line of the report names
# <harness> and carries all three figures. Which of the three is labelled which is the
# script's business; that the group is printed as a band and not as one number is this
# suite's.
band() {
  local harness="$1"
  grep -F "$harness" <<< "$out" |
    grep -E "$(anchored "$2")" | grep -E "$(anchored "$3")" | grep -E "$(anchored "$4")" |
    grep -q . ||
      problems+=("the $harness band: want one line naming $harness and stating min $2, median $3 and max $4 together, no line states all three")
}

band claude-desktop "${want_desktop_preambles[@]}"
band sdk-cli "${want_leaf_preambles[@]}"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"



# 11. The harness of case 10 read one step further: a session whose record carries NO
#     `entrypoint` key at all. That is what a conductor's transcript looks like — veri
#     launches it from a `/tdd` run rather than from a harness of its own, so Claude Code
#     writes no entrypoint on the record — and it is the reading the wrong conclusion of
#     2026-09-15 was made of: 51,986 was taken for a desktop baseline when it was a
#     conductor's, and a report that had folded the key's absence in with the terminal
#     sessions that do carry one would have said the same wrong thing, only in print.
#
#     So an absent key is a KIND and not a missing value: it names the group `conductor`,
#     and its preambles band apart from `cli`'s. The fixture is the two harnesses that
#     collide — a conductor and a terminal session sit 350 tokens apart in one project
#     directory, which is why these two and not the desktop app — three single-request
#     sessions each, at the figures the issue measured on 2026-09-14 → 15:
#
#       conductor (no entrypoint key)  51986  53438  55994
#       cli                            52500  53786  54800
#
#     The two groups INTERLEAVE, which is what stops a report that pooled them from
#     answering here: pooled, the six preambles band as 51986 / 53786 / 55994 — the
#     conductor's min and max with `cli`'s median between them — so the pooled band
#     states neither group's three. A fold in the other direction, one that grouped
#     correctly but called the absent key by the name of the harness beside it, fails on
#     the rows and on the band naming `conductor`.
name="an absent entrypoint is a conductor: its rows and its band are named as such, apart from cli's"
problems=()

# Same shape as case 10's table: <8-char id prefix> <input> <cache write>, preamble their
# sum, read 0 because a preamble is a first request. Each group's preambles are listed
# ascending, so the array is the band the report owes for it.
conductor_ids=(1a842fb0-6d03-4e51-b7c2-8ef1a940d25e
               2b953ec1-7e14-4f62-c8d3-9fa2b051e36f
               3ca64fd2-8f25-4073-d9e4-0ab3c162f470)
conductor_ins=(986 438 994)
conductor_writes=(51000 53000 55000)
want_conductor_preambles=(51986 53438 55994)

cli_ids=(4db75063-9036-4184-e0f5-1bc4d273058a
         5ec86174-0147-4295-f106-2cd5e384169b
         6fd97285-1258-43a6-028f-3de6f495270c)
cli_ins=(500 786 800)
cli_writes=(52000 53000 54000)
want_cli_preambles=(52500 53786 54800)

# One writer taking the entrypoint field as JSON text rather than as a value, because what
# this case is about is a record on which the key is not there at all: a writer that took
# a value could only ever write the key with something in it, including the empty string,
# which is a different record from the one a conductor leaves behind.
transcripts=()
write_keyed_session() {
  local id="$1" entrypoint_field="$2" input="$3" write="$4" stamp="$5" out_tokens="$6"
  local path="$work/$id.jsonl"
  cat > "$path" <<TRANSCRIPT
{"type":"assistant","timestamp":"$stamp","requestId":"req_$id","sessionId":"$id",${entrypoint_field}"userType":"external","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$input,"cache_creation_input_tokens":$write,"cache_creation":{"ephemeral_5m_input_tokens":$write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":0,"output_tokens":$out_tokens}}}
TRANSCRIPT
  transcripts+=("$path")
}

for i in 0 1 2; do
  write_keyed_session "${conductor_ids[$i]}" "" "${conductor_ins[$i]}" "${conductor_writes[$i]}" \
    "2026-09-14T0$i:11:45.310Z" "$((3300 + i))"
  write_keyed_session "${cli_ids[$i]}" '"entrypoint":"cli",' "${cli_ins[$i]}" "${cli_writes[$i]}" \
    "2026-09-14T0$i:48:02.915Z" "$((4400 + i))"
done

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "${transcripts[@]}" 2>&1)"
code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh, got $code")

# The rows: each session is found by its id, as case 10 finds one, and has to be named by
# the harness it belongs to. `conductor` and `cli` share no substring, so a fixed-string
# match on either cannot be answered by the other.
for i in 0 1 2; do
  grep -Fq conductor < <(grep -F "${conductor_ids[$i]:0:8}" <<< "$out") ||
    problems+=("session ${conductor_ids[$i]:0:8}: no entrypoint key, want its row to name it a conductor, it does not")
  grep -Fq cli < <(grep -F "${cli_ids[$i]:0:8}" <<< "$out") ||
    problems+=("session ${cli_ids[$i]:0:8}: want its row to name the entrypoint cli, it does not")
done

# And the two bands, through case 10's `band`: one line per group naming it and carrying
# all three of its figures.
band conductor "${want_conductor_preambles[@]}"
band cli "${want_cli_preambles[@]}"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

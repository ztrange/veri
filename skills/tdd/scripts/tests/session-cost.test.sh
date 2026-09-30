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

source "$HERE/lib/harness.sh"

anchored() {
  printf '(^|[^0-9])%s([^0-9]|$)' "${1//./\\.}"
}

states() {
  local what="$1" where="$3" lines="$4"
  grep -Eq "$(anchored "$2")" <<< "$lines" ||
    problems+=("$what: want $2 on a line $where, not found in the report")
}

figure() {
  states "$1" "$3" "naming it" "$(grep -Ei "$2" <<< "$out")"
}

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

work="$(scratch_dir)"

name="a day's transcript: session-cost.sh totals its cost, split into cache read, cache write and output"
problems=()

transcript="$work/2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4.jsonl"

a_read=800000   ; a_write=200000 ; a_out=15000 ; a_in=3
b_read=440000   ; b_write=128000 ; b_out=8600  ; b_in=1

want_read_cost=1.86
want_write_cost=6.15
want_output_cost=1.77
want_total_cost=9.78

cat > "$transcript" <<TRANSCRIPT
{"type":"summary","summary":"A cost report read from the session transcripts","leafUuid":"0b1f8c22-4a67-4f30-91da-6c2d3e5b7a19"}
{"type":"user","timestamp":"2026-09-14T12:04:28.331Z","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"user","content":"total the day"}}
{"type":"assistant","timestamp":"2026-09-14T12:04:31.807Z","requestId":"req_011CS4kQn7XdF2vHbJ9tLm3p","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$a_in,"cache_creation_input_tokens":$a_write,"cache_creation":{"ephemeral_5m_input_tokens":$a_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$a_read,"output_tokens":$a_out}}}
{"type":"user","timestamp":"2026-09-14T15:37:09.115Z","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"user","content":"and the split"}}
{"type":"assistant","timestamp":"2026-09-14T15:37:12.244Z","requestId":"req_011CS5rB8xWgT6nPqK4vZy7d","sessionId":"2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$b_in,"cache_creation_input_tokens":$b_write,"cache_creation":{"ephemeral_5m_input_tokens":$b_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$b_read,"output_tokens":$b_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

expect_split

report "$name"


name="project directories: every slug prefixed by the repo root's is summed, an unrelated one is not"
problems=()

tree="$(scratch_dir)"
root="$tree/repo"
mkdir -p "$root"
root="$(cd "$root" && pwd -P)"
git -C "$root" init -q 2>/dev/null

home="$tree/home"
projects="$home/.claude/projects"

slug="${root//\//-}"

mkdir -p "$projects/$slug" \
         "$projects/$slug--tdd-wt-999" \
         "$projects/-Users-someone-else-anotherrepo"

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

out="$(cd "$root" && HOME="$home" TZ=UTC "$SESSION_COST" --since 2026-09-14 2>&1)"
code=$?

expect_split

rm -rf "$tree"
report "$name"

name="one request, six records: a repeated requestId is counted once, a distinct one still counts"
problems=()

transcript="$work/6b3e02f7-d914-4c85-a27e-8f01c6b45d3a.jsonl"

a_read=900000 ; a_write=160000 ; a_out=12400 ; a_in=3
b_read=500000 ; b_write=40000  ; b_out=7600  ; b_in=1

want_read_cost=2.10
want_write_cost=3.75
want_output_cost=1.50
want_total_cost=7.35

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

cat >> "$transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T10:09:47.663Z","requestId":"req_011CSAeR6tUvB2hXzF5sMo9a","sessionId":"6b3e02f7-d914-4c85-a27e-8f01c6b45d3a","message":{"role":"assistant","model":"claude-opus-4-1-20250805","content":[{"type":"text","text":"done"}],"usage":{"input_tokens":$b_in,"cache_creation_input_tokens":$b_write,"cache_creation":{"ephemeral_5m_input_tokens":$b_write,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$b_read,"output_tokens":$b_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

expect_split

report "$name"


name="cache-write tiers: 1h and 5m are priced apart, and a bare cache_creation_input_tokens falls back to 5m"
problems=()

transcript="$work/9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5.jsonl"

a_read=200000 ; a_write_1h=400000 ; a_out=4000 ; a_in=1
b_read=100000 ; b_write_5m=400000 ; b_out=2000 ; b_in=1
c_read=60000  ; c_write_flat=200000 ; c_out=2000 ; c_in=1

want_read_cost=0.54
want_write_cost=23.25
want_output_cost=0.60
want_total_cost=24.39

cat > "$transcript" <<TRANSCRIPT
{"type":"assistant","timestamp":"2026-09-14T08:15:03.221Z","requestId":"req_011CSBfS7uVwC3iYaG6tNp0b","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$a_in,"cache_creation_input_tokens":$a_write_1h,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":$a_write_1h},"cache_read_input_tokens":$a_read,"output_tokens":$a_out}}}
{"type":"assistant","timestamp":"2026-09-14T08:41:19.508Z","requestId":"req_011CSCgT8vWxD4jZbH7uOq1c","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$b_in,"cache_creation_input_tokens":$b_write_5m,"cache_creation":{"ephemeral_5m_input_tokens":$b_write_5m,"ephemeral_1h_input_tokens":0},"cache_read_input_tokens":$b_read,"output_tokens":$b_out}}}
{"type":"assistant","timestamp":"2026-09-14T09:03:55.740Z","requestId":"req_011CSDhU9wXyE5kAcI8vPr2d","sessionId":"9d4c71b0-2e86-4a13-b5f7-0c38e1d2a6f5","message":{"role":"assistant","model":"claude-opus-4-1-20250805","usage":{"input_tokens":$c_in,"cache_creation_input_tokens":$c_write_flat,"cache_read_input_tokens":$c_read,"output_tokens":$c_out}}}
TRANSCRIPT

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$transcript" 2>&1)"
code=$?

expect_split

report "$name"


name="--since: a record before the window is excluded, one inside it is counted"
problems=()

transcript="$work/c5a8f30d-9b71-42e6-8d04-5f71e9b2c6a7.jsonl"

before_read=300000 ; before_write=80000  ; before_out=6800 ; before_in=2
inside_read=700000 ; inside_write=120000 ; inside_out=9200 ; inside_in=2

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


name="roles: an sdk-cli session and an interactive session are attributed to their own rows"
problems=()

leaf_transcript="$work/3f6d9a71-0c58-4e29-b7a3-1d4e8f2c50b6.jsonl"
human_transcript="$work/7a1c4e82-6b30-4d95-8f16-2e9b0a5d3c74.jsonl"

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

figure "the sdk-cli session's row"     'sdk-cli|leaf'  "$want_leaf_cost"
figure "the interactive session's row" 'interactive'   "$want_human_cost"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


name="per-session rows: preamble, final and total context, and an un-cleared ramp named in words"
problems=()

ramp_transcript="$work/a8f3d1c6-4b27-4e50-9a83-7f0d2e6c19b5.jsonl"
flat_transcript="$work/5c72e0b4-9d18-4a36-b7e2-0f45c8a13d9e.jsonl"

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

session_figure() {
  states "$1" "$3" "naming session $2" "$(grep -F "$2" <<< "$out")"
}

session_figure "the ramping session's preamble"      a8f3d1c6 "$want_ramp_preamble"
session_figure "the ramping session's final context" a8f3d1c6 "$want_ramp_final"
session_figure "the ramping session's context read"  a8f3d1c6 "$want_ramp_total"

session_figure "the flat session's preamble"         5c72e0b4 "$want_flat_preamble"
session_figure "the flat session's final context"    5c72e0b4 "$want_flat_final"
session_figure "the flat session's context read"     5c72e0b4 "$want_flat_total"

ramp_words='un-?cleared|never cleared|not cleared|ramp'

grep -Eqi "$ramp_words" < <(grep -F a8f3d1c6 <<< "$out") ||
  problems+=("the ramping session: want its row to name it as un-cleared in words, matching /$ramp_words/, not found")

! grep -Eqi "$ramp_words" < <(grep -F 5c72e0b4 <<< "$out") ||
  problems+=("the flat session: its context read is exactly its preamble x its requests, so it must NOT be named as un-cleared, but a line naming it matches /$ramp_words/")

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


name="an unknown model: its tokens are reported, its cost is blank, and it is named in a footer"
problems=()

known_transcript="$work/1d8b6f40-2a93-4c17-8e65-3b07d9a4f2e1.jsonl"
unknown_transcript="$work/9e4a2c58-7f61-4b0d-a392-5c81e6b70d43.jsonl"

known_read=600000 ; known_write=40000 ; known_out=4400 ; known_in=2

want_read_cost=0.90
want_write_cost=0.75
want_output_cost=0.33
want_total_cost=1.98

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

footer="$(grep -F "$unknown_model" <<< "$out")"

[[ -n "$footer" ]] ||
  problems+=("the unknown model: want a line naming $unknown_model, the report names it nowhere")

states "the unknown model's tokens" "$want_unknown_tokens" "naming $unknown_model" "$footer"

! grep -Eq '\$[0-9]' <<< "$footer" ||
  problems+=("the unknown model: want no money on the line naming it, got $(printf '%q' "$footer")")

expect_split

report "$name"


name="--json: the machine output states the same four totals as the text report"
problems=()

json_transcript="$work/6b19d4e7-3c05-42af-9d71-8e260a5fb3c7.jsonl"

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

out="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 "$json_transcript" 2>&1)"
code=$?

expect_split

json_err="$work/json.err"
out_json="$(TZ=UTC "$SESSION_COST" --since 2026-09-14 --json "$json_transcript" 2>"$json_err")"
json_code=$?

[[ "$json_code" == 0 ]] ||
  problems+=("want exit 0 from session-cost.sh --json, got $json_code; stderr was: $(printf '%q' "$(cat "$json_err")")")

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


name="harness baselines: every session row names its entrypoint, and the bands are min / median / max per harness"
problems=()

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

row_names() {
  grep -Fq "$2" < <(grep -F "${1:0:8}" <<< "$out")
}

for i in 0 1 2; do
  row_names "${desktop_ids[$i]}" claude-desktop ||
    problems+=("session ${desktop_ids[$i]:0:8}: want its row to name the entrypoint claude-desktop, it does not")
  row_names "${leaf_ids[$i]}" sdk-cli ||
    problems+=("session ${leaf_ids[$i]:0:8}: want its row to name the entrypoint sdk-cli, it does not")
done

band() {
  local harness="$1"
  grep -F "$harness" <<< "$out" |
    grep -E "$(anchored "$2")" | grep -E "$(anchored "$3")" | grep -E "$(anchored "$4")" |
    grep . > /dev/null ||
      problems+=("the $harness band: want one line naming $harness and stating min $2, median $3 and max $4 together, no line states all three")
}

band claude-desktop "${want_desktop_preambles[@]}"
band sdk-cli "${want_leaf_preambles[@]}"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"



name="an absent entrypoint is a conductor: its rows and its band are named as such, apart from cli's"
problems=()

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

for i in 0 1 2; do
  row_names "${conductor_ids[$i]}" conductor ||
    problems+=("session ${conductor_ids[$i]:0:8}: no entrypoint key, want its row to name it a conductor, it does not")
  row_names "${cli_ids[$i]}" cli ||
    problems+=("session ${cli_ids[$i]:0:8}: want its row to name the entrypoint cli, it does not")
done

band conductor "${want_conductor_preambles[@]}"
band cli "${want_cli_preambles[@]}"

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$out")")

report "$name"


finish

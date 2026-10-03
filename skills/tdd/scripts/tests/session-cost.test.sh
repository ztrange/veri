#!/usr/bin/env bash
# Unit tests for scripts/session-cost.sh — the cost report read from the session
# transcripts.
#
# Contract under test:
#   session-cost.sh --since <ISO date> [<transcript.jsonl>]
#     → exit 0, and a report on stdout whose money is split three ways — what the cache
#       READS cost, what the cache WRITES cost, what the OUTPUT cost — and totalled. With
#       a transcript named, that one file is the day; with none, the day is every project
#       directory under `$HOME/.claude/projects` whose slug is prefixed by the repo root's.
#   Prices are per million tokens: $1.50 cache read, $18.75 cache write at the 5m TTL,
#   $30.00 at the 1h one, $75.00 output, $15.00 input.
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

name="given a nonexistent transcript, session-cost.sh exits 2 with its own usage text on stderr"
problems=()

missing_err="$work/missing-transcript.err"
"$SESSION_COST" --since 2026-09-14 "$work/no-such-transcript.jsonl" > /dev/null 2>"$missing_err"
code=$?

[[ "$code" == 2 ]] ||
  problems+=("want exit 2 from session-cost.sh, got $code")
grep -F 'usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]' "$missing_err" > /dev/null ||
  problems+=("want its usage text on stderr, stderr was: $(printf '%q' "$(cat "$missing_err")")")

report "$name"

name="given an unknown option, session-cost.sh exits 2 with its own usage text on stderr"
problems=()

unknown_err="$work/unknown-option.err"
"$SESSION_COST" --since 2026-09-14 --no-such-option > /dev/null 2>"$unknown_err"
code=$?

[[ "$code" == 2 ]] ||
  problems+=("want exit 2 from session-cost.sh, got $code")
grep -F 'usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]' "$unknown_err" > /dev/null ||
  problems+=("want its usage text on stderr, stderr was: $(printf '%q' "$(cat "$unknown_err")")")

report "$name"

name="session-cost.sh run through a symlink to the skill directory and from another working directory prints the same report and exit code as when run in place"
problems=()

day="$work/2f7b41a9-6c30-4d8e-9f02-1a55c7e3b8d4.jsonl"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"

in_place="$(cd "$HERE/.." && TZ=UTC ./session-cost.sh --since 2026-09-14 "$day" 2>&1)"
in_place_code=$?
linked="$(cd "$work/elsewhere" && TZ=UTC "$work/linked-skill/scripts/session-cost.sh" --since 2026-09-14 "$day" 2>&1)"
linked_code=$?

[[ "$in_place_code" == 0 && "$in_place" == *9.78* ]] ||
  problems+=("want the in-place run to exit 0 with a 9.78 total, got exit $in_place_code: $(printf '%q' "$in_place")")
[[ "$linked" == "$in_place" && "$linked_code" == "$in_place_code" ]] ||
  problems+=("$(diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code"))")

report "$name"


finish

#!/usr/bin/env bash
# Unit tests for scripts/red-divergence.sh — the pure transform that reads a develop-red
# or revise-red leaf's report on stdin and says whether its prediction diverged, so the
# conductor can stop on the surprise instead of sending the step to a blind verify-red.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   stdin  = the leaf's report (the PREDICTED_FAILURE:/PREDICTION:/… lines at its end)
#   stdout = on DIVERGED, a reason carrying the report's PREDICTED_FAILURE:, FAIL_OUTPUT:
#            and PREDICTION_NOTE: values, which is what the conductor writes to
#            .tdd/verify-red.reason for the revise leaf to read
#   exit   = 0 DIVERGED · 3 MATCHED (nothing to do) · 2 no readable PREDICTION:
#
# Run: scripts/tests/unit/red-divergence.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DIVERGENCE="$HERE/../../red-divergence.sh"
source "$HERE/../lib/harness.sh"

run_on() {
  out="$(printf '%s' "$1" | "$DIVERGENCE" 2>&1)" && code=0 || code=$?
}

verdict() {
  local name="$1" p
  if (( ${#problems[@]} )); then
    no "$name"
    for p in "${problems[@]}"; do echo "    $p"; done
  else
    ok
  fi
}

predicted='slugify: command not found'
fail_output='FAIL - slugify lowercases the title (want exit 0, got 127)'
note='the suite died on a missing helper before it reached the assertion'

leaf_report() {
  local text line
  text="TEST_PATH: skills/tdd/scripts/tests/unit/slugify.test.sh
TARGET_TEST: slugify lowercases the title
AGAINST_UNMODIFIED: FAILS
FAIL_OUTPUT: $1
PREDICTED_FAILURE: $2"
  for line in "${@:3}"; do text+="
$line"; done
  printf '%s' "$text"
}

as_predicted_report() {
  leaf_report "FAIL - slugify lowercases the title (want 'a-b', got 'A B')" \
         "the assertion on the slug, want 'a-b', got 'A B'" "$@"
}

surprise_report() {
  leaf_report "$fail_output" "$predicted" "$@"
}

reads_matched() {
  run_on "$(as_predicted_report "$1")"
  [[ "$code" == 3 ]] || problems+=("$1: want exit 3, got $code")
  [[ -z "$out" ]] || problems+=("$1: want no output, got '$(printf '%s' "$out" | tr '\n' '|')'")
}

reads_diverged() {
  run_on "$(surprise_report "$1" "PREDICTION_NOTE: $note")"
  [[ "$code" == 0 ]] || problems+=("$1: want exit 0, got $code")
  [[ "$out" == *"$note"* ]] || problems+=("$1: stdout does not carry the PREDICTION_NOTE value '$note'")
}

reads_unreadable() {
  run_on "$(as_predicted_report "$@")"
  [[ "$code" == 2 ]] || problems+=("${1:-no PREDICTION: line}: want exit 2, got $code")
}

name="DIVERGED report exits 0 and prints its PREDICTED_FAILURE, FAIL_OUTPUT and PREDICTION_NOTE"
problems=()
reads_diverged 'PREDICTION: DIVERGED'
[[ "$out" == *"$predicted"* ]] || problems+=("stdout does not carry the PREDICTED_FAILURE value '$predicted'")
[[ "$out" == *"$fail_output"* ]] || problems+=("stdout does not carry the FAIL_OUTPUT value '$fail_output'")
if (( ${#problems[@]} )); then problems+=("it printed: $(printf '%s' "$out" | tr '\n' '|')"); fi
verdict "$name"

name="MATCHED report exits 3 and prints nothing"
problems=()
reads_matched 'PREDICTION: MATCHED'
verdict "$name"

name="report with no PREDICTION: line, or an unrecognised value, exits 2"
problems=()
reads_unreadable
reads_unreadable 'PREDICTION: probably'
verdict "$name"

name="PREDICTION line with a trailing clause after the verdict word is read as that verdict"
problems=()
reads_matched 'PREDICTION: MATCHED — the run printed the assertion the step predicted'
reads_diverged 'PREDICTION: DIVERGED — it died on a missing helper instead'
verdict "$name"

name="PREDICTION line whose first word is not a verdict exits 2 even when a verdict word follows"
problems=()
reads_unreadable 'PREDICTION: probably MATCHED, hard to say'
verdict "$name"

prompt_verdicts() {
  local line alts offered_verdict
  local -a offers
  while IFS= read -r line; do
    alts="${line#PREDICTION: }"
    alts="${alts%% — *}"
    IFS='|' read -r -a offers <<< "$alts"
    for offered_verdict in "${offers[@]}"; do
      offered_verdict="${offered_verdict#"${offered_verdict%%[![:space:]]*}"}"
      offered_verdict="${offered_verdict%"${offered_verdict##*[![:space:]]}"}"
      [[ -n "$offered_verdict" ]] || continue
      printf '%s\n' "$offered_verdict"
    done
  done < <(grep '^PREDICTION: ' "$1")
}

name="every verdict the leaf prompts offer on their PREDICTION: line is one the parser reads"
problems=()
prompts_dir="$HERE/../../prompts"
offered=0
for prompt in "$prompts_dir"/*.md; do
  while IFS= read -r offered_verdict; do
    offered=$((offered + 1))
    run_on "$(as_predicted_report "PREDICTION: $offered_verdict")"
    [[ "$code" != 2 ]] || problems+=("$(basename "$prompt") offers '$offered_verdict' and the parser reads it as no verdict at all (exit 2)")
  done < <(prompt_verdicts "$prompt")
done
(( offered )) || problems+=("no prompt under $prompts_dir carries a PREDICTION: report line to check")
verdict "$name"

name="PREDICTION verdict word carrying trailing punctuation is read as that verdict"
problems=()
for mark in ',' ';' ':' '.'; do
  reads_matched "PREDICTION: MATCHED$mark but only in the message"
  reads_diverged "PREDICTION: DIVERGED$mark but only in the message"
done
verdict "$name"

name="PREDICTION line whose first word is not a verdict once its punctuation is stripped exits 2"
problems=()
for mark in ',' ';' ':' '.'; do
  reads_unreadable "PREDICTION: probably$mark MATCHED anyway"
done
verdict "$name"

name="report with no PREDICTION: line exits 2 with nothing on stdout and nothing on stderr"
problems=()
streams="$(scratch_dir)"
as_predicted_report | "$DIVERGENCE" > "$streams/stdout" 2> "$streams/stderr" && code=0 || code=$?
[[ "$code" == 2 ]] || problems+=("want exit 2, got $code")
[[ ! -s "$streams/stdout" ]] || problems+=("want nothing on stdout, got '$(tr '\n' '|' < "$streams/stdout")'")
[[ ! -s "$streams/stderr" ]] || problems+=("want nothing on stderr, got '$(tr '\n' '|' < "$streams/stderr")'")
verdict "$name"

finish

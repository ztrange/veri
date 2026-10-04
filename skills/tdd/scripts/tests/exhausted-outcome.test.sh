#!/usr/bin/env bash
# Unit tests for scripts/exhausted-outcome.sh — reads the report of the leaf sent when a
# step's revise budget ran out, and says which of the three outcomes that report holds.
#
# Contract under test:
#   stdin  = the exhausted leaf's full raw output (free-form reasoning + its report lines)
#   stdout = the SPLIT: criteria, one per line · or the needs-user answer · or nothing
#   exit   = 0 split · 1 needs the user · 3 neither (nothing to do, not an error)
#
# Run: scripts/tests/exhausted-outcome.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUTCOME="$HERE/../exhausted-outcome.sh"
source "$HERE/lib/harness.sh"

out="" code=0
run() { out="$(printf '%s' "$1" | "$OUTCOME")" && code=0 || code=$?; }

problems=""

split_report='The step names four behaviours at once, so no one green could carry it.
SPLIT: detect-test-command.sh exits 2 on an unknown --mode value
SPLIT: detect-test-command.sh exits 2 when given both an issue and --all'
split_want='detect-test-command.sh exits 2 on an unknown --mode value
detect-test-command.sh exits 2 when given both an issue and --all'
run "$split_report"
[[ "$code" -eq 0 ]] || problems="$problems; a SPLIT: report exited $code, want 0"
[[ "$out" == "$split_want" ]] || problems="$problems; a SPLIT: report printed '$out', want '$split_want'"

user_report='This one is not a split: the criterion contradicts the step before it.
NEEDS_USER: step 2 says exit 1 and step 4 says exit 2 for the same refusal — which wins is a
decision this run has no authority to make.'
user_want='step 2 says exit 1 and step 4 says exit 2 for the same refusal — which wins is a
decision this run has no authority to make.'
run "$user_report"
[[ "$code" -eq 1 ]] || problems="$problems; a NEEDS_USER: report exited $code, want 1"
[[ "$out" == "$user_want" ]] || problems="$problems; a NEEDS_USER: report printed '$out', want '$user_want'"

neither_report='I read the step and the rejection reason and I am not sure what to make of them.'
run "$neither_report"
[[ "$code" -eq 3 ]] || problems="$problems; a report holding neither exited $code, want 3"
[[ -z "$out" ]] || problems="$problems; a report holding neither printed '$out'"

[[ -z "$problems" ]] \
  && ok || no "exhausted-outcome answers exit 0 with the SPLIT: criteria, exit 1 with the needs-user answer, exit 3 and nothing for neither (${problems#; })"

problems=""
err_file="$(mktemp)"
args_out="$(printf 'SPLIT: a' | "$OUTCOME" extra args 2>"$err_file")" && args_code=0 || args_code=$?
[[ "$args_code" -eq 0 ]] || problems="$problems; called with extra args it exited $args_code, want 0"
[[ "$args_out" == "a" ]] || problems="$problems; called with extra args it printed '$args_out', want 'a'"
[[ ! -s "$err_file" ]] || problems="$problems; called with extra args it wrote '$(cat "$err_file")' on stderr"
for report in 'SPLIT: a' 'NEEDS_USER: q' 'neither'; do
  printf '%s' "$report" | "$OUTCOME" >/dev/null 2>"$err_file" || true
  [[ ! -s "$err_file" ]] || problems="$problems; '$report' wrote '$(cat "$err_file")' on stderr"
done
rm -f "$err_file"

[[ -z "$problems" ]] \
  && ok || no "exhausted-outcome ignores its arguments and never writes to stderr (${problems#; })"

finish

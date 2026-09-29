#!/usr/bin/env bash
# Unit tests for scripts/exhausted-outcome.sh — the pure transform that reads the report of
# the leaf sent when a step's revise budget ran out (issue #408), and says which of the three
# outcomes that report holds. Zero-dependency plain-shell asserts, same idiom as
# parse-verdict.test.sh, whose contract this one mirrors: stdin is a leaf's raw output, and
# the exit code is the answer the conductor branches on.
#
# Contract under test:
#   stdin  = the exhausted leaf's full raw output (free-form reasoning + its report lines)
#   stdout = the SPLIT: criteria, one per line · or the needs-user answer · or nothing
#   exit   = 0 split · 1 needs the user · 3 neither (nothing to do, not an error)
#
# Run: scripts/tests/exhausted-outcome.test.sh   (exits non-zero if any case fails)
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUTCOME="$HERE/../exhausted-outcome.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

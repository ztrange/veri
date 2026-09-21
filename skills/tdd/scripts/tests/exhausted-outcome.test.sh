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

# 1. the three outcomes one exhausted leaf may report (issue #408). A step whose revise budget
#    ran out is sent one last leaf, asked which of two things is true of the criterion nothing
#    could satisfy: that it carries more than one behaviour (`SPLIT:` lines, the condition Green
#    already splits on), or that it needs a decision the run has no authority to make
#    (`NEEDS_USER:`). Answering neither is the third outcome, and it is not an error — the
#    conductor bails the step exactly as it does today. The three are one contract, so one case:
#    which outcome a report holds and what the conductor is handed for it are the same question,
#    and the three exits are only meaningful against each other. Exit 3 is veri's "nothing to
#    do", never 2, because a leaf that volunteered neither answer is an answer, not a plumbing
#    failure. The criteria come back as their bare texts, one per line, because add-ledger-step.sh
#    takes them as positional arguments; the needs-user text comes back verbatim because it is
#    what the user reads on the issue.
problems=""

split_report='The step names four behaviours at once, so no one green could carry it.
SPLIT: detect-test-command.sh exits 2 on an unknown --mode value
SPLIT: detect-test-command.sh exits 2 when given both an issue and --all'
split_out="$(printf '%s' "$split_report" | "$OUTCOME")" && split_code=0 || split_code=$?
split_want='detect-test-command.sh exits 2 on an unknown --mode value
detect-test-command.sh exits 2 when given both an issue and --all'
[[ "$split_code" -eq 0 ]] || problems="$problems; a SPLIT: report exited $split_code, want 0"
[[ "$split_out" == "$split_want" ]] || problems="$problems; a SPLIT: report printed '$split_out', want '$split_want'"

user_report='This one is not a split: the criterion contradicts the step before it.
NEEDS_USER: step 2 says exit 1 and step 4 says exit 2 for the same refusal — which wins is a
decision this run has no authority to make.'
user_want='step 2 says exit 1 and step 4 says exit 2 for the same refusal — which wins is a
decision this run has no authority to make.'
user_out="$(printf '%s' "$user_report" | "$OUTCOME")" && user_code=0 || user_code=$?
[[ "$user_code" -eq 1 ]] || problems="$problems; a NEEDS_USER: report exited $user_code, want 1"
[[ "$user_out" == "$user_want" ]] || problems="$problems; a NEEDS_USER: report printed '$user_out', want '$user_want'"

neither_report='I read the step and the rejection reason and I am not sure what to make of them.'
neither_out="$(printf '%s' "$neither_report" | "$OUTCOME")" && neither_code=0 || neither_code=$?
[[ "$neither_code" -eq 3 ]] || problems="$problems; a report holding neither exited $neither_code, want 3"
[[ -z "$neither_out" ]] || problems="$problems; a report holding neither printed '$neither_out'"

[[ -z "$problems" ]] \
  && ok || no "exhausted-outcome answers exit 0 with the SPLIT: criteria, exit 1 with the needs-user answer, exit 3 and nothing for neither (${problems#; })"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

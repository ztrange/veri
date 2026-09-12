#!/usr/bin/env bash
# Unit tests for the workflow files under .github/workflows/ — they belong to no script,
# so like hermetic-suites.test.sh this suite has no single subject: it reads the YAML the
# way GitHub Actions does, as text, and asserts on what a job declares.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists (issue #99): a job with no `timeout-minutes` inherits GitHub's default
# ceiling of 6 hours, so a hang bills every minute of it (~$2.16 on Linux) while looking
# exactly like a slow run. The cap turns that into a bounded bill and a red tick — and
# the number only stays right while the reason for it is written down next to it, which
# is why the comment is part of the contract and not decoration.
#
# Contract under test:
#   .github/workflows/ci.yml, the `gates` job: `timeout-minutes: 3` at job level, and the
#   comment beside it names the 6-hour ceiling it protects against, cites the ~40 s the
#   job observably takes and the ~230 s it took while the docs gates ran in CI, and says
#   the budget assumes those gates stay out of CI.
#
#   .github/workflows/pages.yml, the `deploy` job: `timeout-minutes: 10` at job level, and
#   the comment beside it names the same 6-hour ceiling, cites the 11–23 s the job
#   observably takes, and says why its number is larger than the gates job's — it waits on
#   GitHub's Pages service rather than on local deterministic work.
#
# Run: scripts/tests/workflow-timeouts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
CI_YML="$ROOT/.github/workflows/ci.yml"
PAGES_YML="$ROOT/.github/workflows/pages.yml"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# probe <message> <regex>... — one fact the comment under test has to carry, written as the
# regexes that would show it is there: all of them have to match, and `message` names the
# fact once if any does not. Reads `$lc` and appends to `$problems`, the way report() reads
# `$problems` — the subject of every probe in this suite is the same lowercased comment.
# Each regex accepts any wording that carries the fact, so a case pins what the comment
# says and not how it is phrased.
probe() {
  local msg="$1"; shift
  local re
  for re in "$@"; do
    [[ "$lc" =~ $re ]] || { problems+=("$msg"); return; }
  done
}

# job_block <file> <job> -> the lines that belong to one job's mapping, on stdout.
# A job key sits at indent 2 under `jobs:` and everything of its own is indented further,
# so the block runs from the line after `  <job>:` to the next line that starts at indent
# 2 — the next job. Scoping to the block is what makes "the gates job declares it" a
# different assertion from "the file mentions it somewhere".
job_block() {
  awk -v key="  $2:" '
    $0 == key { inside = 1; next }
    inside && /^  [^ ]/ { exit }
    inside { print }
  ' "$1"
}

# timeout_comment <file> <job> <minutes> — locate that job's own `timeout-minutes: <minutes>`
# and set `$lc` to the lowercased comment beside it, which is what every probe() reads.
# Returns non-zero, with the reason appended to `$problems`, when there is no comment to
# read. Three states, each with its own message and only one of them reported: no job at
# all, a job without the declaration, or the declaration to read the comment around. A
# missing job would otherwise also report as a missing timeout, which is true but says the
# wrong thing about what to go fix.
timeout_comment() {
  local file="$1" job="$2" minutes="$3"
  local line n idx i j ctx re
  local -a block
  block=()
  while IFS= read -r line; do block+=("$line"); done < <(job_block "$file" "$job")
  n="${#block[@]}"

  # The declaration has to be the job's own, not a step's: job keys in these files sit at
  # indent 4, beside `runs-on`. A trailing comment on the same line is allowed — that is
  # one of the two shapes "a comment beside it" can take.
  re="^    timeout-minutes:[ ]*${minutes}[ ]*(#.*)?$"
  idx=-1
  i=0
  while [[ "$i" -lt "$n" ]]; do
    if [[ "${block[$i]}" =~ $re ]]; then idx="$i"; break; fi
    i=$((i + 1))
  done

  if [[ "$n" -eq 0 ]]; then
    problems+=("no $job job found in $file")
    return 1
  fi
  if [[ "$idx" -lt 0 ]]; then
    problems+=("$job job declares no job-level 'timeout-minutes: $minutes'")
    return 1
  fi

  # "Beside it" is the timeout line itself plus the run of comment lines directly above
  # it — the register both workflow headers already use for a decision that needs a why.
  ctx="${block[$idx]}"
  j=$((idx - 1))
  while [[ "$j" -ge 0 ]] && [[ "${block[$j]}" =~ ^[[:space:]]*# ]]; do
    ctx="${block[$j]}"$'\n'"$ctx"
    j=$((j - 1))
  done
  lc="$(printf '%s' "$ctx" | tr 'A-Z' 'a-z')"
}

# 1. The contract above. The four facts in the comment are one criterion — the number is
#    only defensible with its reasoning beside it — so they report as one case, with
#    `problems` naming whichever fact is missing.
name="ci.yml gates: timeout-minutes 3, with a comment citing the 6-hour ceiling, ~40 s, ~230 s, and docs gates staying out of CI"
problems=()

if timeout_comment "$CI_YML" gates 3; then
  probe "comment beside the timeout does not name the 6-hour default ceiling" \
    '(6[ -]?h|six[ -]?hour)'
  probe "comment does not cite the ~40 s the job observably takes" \
    '(^|[^0-9])(3[0-9]|4[0-9])[ -]?s'
  probe "comment does not cite the ~230 s the job took when the docs gates ran in CI" \
    '(2[0-9][0-9][ -]?s|3\.8[ -]?min)'
  probe "comment does not say the budget assumes the docs gates stay out of CI" \
    'docs' '(out of ci|outside ci|not in ci|stay out|stays out)'
fi
report "$name"

# 2. The same shape for the other workflow: the `deploy` job in pages.yml caps at 10, and
#    its comment has to carry the three facts that make 10 the right number rather than a
#    copy of the gates job's 3 — the ceiling it protects against, the duration it leaves
#    headroom over, and why this job's budget is the larger one.
name="pages.yml deploy: timeout-minutes 10, with a comment citing the 6-hour ceiling, 11-23 s, and why it is larger than gates"
problems=()

if timeout_comment "$PAGES_YML" deploy 10; then
  probe "comment beside the timeout does not name the 6-hour default ceiling" \
    '(6[ -]?h|six[ -]?hour)'
  probe "comment does not cite the 11-23 s the job observably takes" \
    '(^|[^0-9])11([^0-9]|$)' '23[ -]?s'
  probe "comment does not say the job waits on GitHub's Pages service" \
    '(wait|waits|waiting)' 'pages'
  probe "comment does not say why its budget is larger than the gates job's" \
    '(gates|local|deterministic)' '(larger|longer|bigger|generous|more than)'
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

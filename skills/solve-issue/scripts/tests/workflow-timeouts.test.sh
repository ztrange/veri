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
# Run: scripts/tests/workflow-timeouts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
CI_YML="$ROOT/.github/workflows/ci.yml"
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

# 1. The contract above. The four facts in the comment are one criterion — the number is
#    only defensible with its reasoning beside it — so they report as one case, with
#    `problems` naming whichever fact is missing.
name="ci.yml gates: timeout-minutes 3, with a comment citing the 6-hour ceiling, ~40 s, ~230 s, and docs gates staying out of CI"
problems=()

block=()
while IFS= read -r line; do block+=("$line"); done < <(job_block "$CI_YML" gates)
n="${#block[@]}"
[[ "$n" -gt 0 ]] ||
  problems+=("no gates job found in $CI_YML")

# The declaration has to be the job's own, not a step's: job keys in this file sit at
# indent 4, beside `runs-on`. A trailing comment on the same line is allowed — that is
# one of the two shapes "a comment beside it" can take.
timeout_re='^    timeout-minutes:[ ]*3[ ]*(#.*)?$'
idx=-1
i=0
while [[ "$i" -lt "$n" ]]; do
  if [[ "${block[$i]}" =~ $timeout_re ]]; then idx="$i"; break; fi
  i=$((i + 1))
done

if [[ "$idx" -lt 0 ]]; then
  [[ "$n" -eq 0 ]] ||
    problems+=("gates job declares no job-level 'timeout-minutes: 3'")
else
  # "Beside it" is the timeout line itself plus the run of comment lines directly above
  # it — the register both workflow headers already use for a decision that needs a why.
  ctx="${block[$idx]}"
  j=$((idx - 1))
  while [[ "$j" -ge 0 ]] && [[ "${block[$j]}" =~ ^[[:space:]]*# ]]; do
    ctx="${block[$j]}"$'\n'"$ctx"
    j=$((j - 1))
  done
  lc="$(printf '%s' "$ctx" | tr 'A-Z' 'a-z')"

  # Each probe accepts any wording that carries the fact, so the case pins what the
  # comment says and not how it is phrased.
  ceiling_re='(6[ -]?h|six[ -]?hour)'
  [[ "$lc" =~ $ceiling_re ]] ||
    problems+=("comment beside the timeout does not name the 6-hour default ceiling")

  observed_re='(^|[^0-9])(3[0-9]|4[0-9])[ -]?s'
  [[ "$lc" =~ $observed_re ]] ||
    problems+=("comment does not cite the ~40 s the job observably takes")

  docs_era_re='(2[0-9][0-9][ -]?s|3\.8[ -]?min)'
  [[ "$lc" =~ $docs_era_re ]] ||
    problems+=("comment does not cite the ~230 s the job took when the docs gates ran in CI")

  out_of_ci_re='(out of ci|outside ci|not in ci|stay out|stays out)'
  if ! [[ "$lc" == *docs* && "$lc" =~ $out_of_ci_re ]]; then
    problems+=("comment does not say the budget assumes the docs gates stay out of CI")
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

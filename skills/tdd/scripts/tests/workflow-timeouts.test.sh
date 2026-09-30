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
#   .github/workflows/ci.yml, the `gates` job: `timeout-minutes: 5` at job level, and the
#   comment beside it names the 6-hour ceiling it protects against, cites the ~160-175 s the
#   job observably takes and the ~230 s it took while the docs gates ran in CI, says the 5 is
#   temporary until #282 and #290 land, and says
#   the budget assumes those gates stay out of CI.
#
#   .github/workflows/pages.yml, the `deploy` job: `timeout-minutes: 10` at job level, and
#   the comment beside it names the same 6-hour ceiling, cites the 11–23 s the job
#   observably takes, and says why its number is larger than the gates job's — it waits on
#   GitHub's Pages service rather than on local deterministic work.
#
#   And, across every workflow file rather than those two jobs by name: every job declares
#   a job-level `timeout-minutes` at all. That is the half of the contract a job added
#   later can break.
#
# Run: scripts/tests/workflow-timeouts.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
CI_YML="$ROOT/.github/workflows/ci.yml"
PAGES_YML="$ROOT/.github/workflows/pages.yml"

source "$HERE/lib/harness.sh"

probe() {
  local msg="$1"; shift
  local re
  for re in "$@"; do
    [[ "$lc" =~ $re ]] || { problems+=("$msg"); return; }
  done
}

probe_ceiling() {
  probe "comment beside the timeout does not name the 6-hour default ceiling" \
    '(6[ -]?h|six[ -]?hour)'
}

job_block() {
  awk -v key="  $2:" '
    $0 == key { inside = 1; next }
    inside && /^  [^ ]/ { exit }
    inside { print }
  ' "$1"
}

job_names() {
  awk '
    /^jobs:[[:space:]]*$/ { inside = 1; next }
    inside && /^[^[:space:]]/ { exit }
    inside && /^  [A-Za-z0-9_.-]+:[[:space:]]*$/ {
      sub(/:[[:space:]]*$/, ""); sub(/^  /, ""); print
    }
  ' "$1"
}

timeout_comment() {
  local file="$1" job="$2" minutes="$3"
  local line n idx i j ctx re
  local -a block
  block=()
  while IFS= read -r line; do block+=("$line"); done < <(job_block "$file" "$job")
  n="${#block[@]}"

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

  ctx="${block[$idx]}"
  j=$((idx - 1))
  while [[ "$j" -ge 0 ]] && [[ "${block[$j]}" =~ ^[[:space:]]*# ]]; do
    ctx="${block[$j]}"$'\n'"$ctx"
    j=$((j - 1))
  done
  lc="$(printf '%s' "$ctx" | tr 'A-Z' 'a-z')"
}

name="ci.yml gates: timeout-minutes 5, with a comment citing the 6-hour ceiling, the measured 160-175 s, ~230 s, the temporary raise, and docs gates staying out of CI"
problems=()

if timeout_comment "$CI_YML" gates 5; then
  probe_ceiling
  probe "comment does not cite the measured 160-175 s the job takes" \
    '(^|[^0-9])(1[5-9][0-9])[ -]?s'
  probe "comment does not say the 5 is temporary, naming what has to land first" \
    'temporar' '(#282|#290)'
  probe "comment does not cite the ~230 s the job took when the docs gates ran in CI" \
    '(2[0-9][0-9][ -]?s|3\.8[ -]?min)'
  probe "comment does not say the budget assumes the docs gates stay out of CI" \
    'docs' '(out of ci|outside ci|not in ci|stay out|stays out)'
fi
report "$name"

name="pages.yml deploy: timeout-minutes 10, with a comment citing the 6-hour ceiling, 11-23 s, and why it is larger than gates"
problems=()

if timeout_comment "$PAGES_YML" deploy 10; then
  probe_ceiling
  probe "comment does not cite the 11-23 s the job observably takes" \
    '(^|[^0-9])11([^0-9]|$)' '23[ -]?s'
  probe "comment does not say the job waits on GitHub's Pages service" \
    '(wait|waits|waiting)' 'pages'
  probe "comment does not say why its budget is larger than the gates job's" \
    '(gates|local|deterministic)' '(larger|longer|bigger|generous|more than)'
fi
report "$name"

name="every job in every .github/workflows file declares a job-level timeout-minutes"
problems=()

wf_seen=0
for wf in "$ROOT"/.github/workflows/*.yml "$ROOT"/.github/workflows/*.yaml; do
  [[ -f "$wf" ]] || continue
  wf_seen=$((wf_seen + 1))
  jobs_seen=0
  while IFS= read -r job; do
    [[ -n "$job" ]] || continue
    jobs_seen=$((jobs_seen + 1))
    grep -qE '^    timeout-minutes:[ ]*[0-9]+' < <(job_block "$wf" "$job") \
      || problems+=("${wf##*/}: job '$job' declares no job-level timeout-minutes")
  done < <(job_names "$wf")
  [[ "$jobs_seen" -gt 0 ]] || problems+=("${wf##*/}: no jobs found — the sweep read nothing")
done
[[ "$wf_seen" -gt 0 ]] || problems+=("no workflow files found under .github/workflows/")

report "$name"

finish

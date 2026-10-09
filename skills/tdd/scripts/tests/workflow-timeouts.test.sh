#!/usr/bin/env bash
# Unit tests for the workflow files under .github/workflows/, read as text the way GitHub
# Actions reads them.
#
# Contract under test:
#   .github/workflows/ci.yml, the `gates` job: `timeout-minutes: 8` at job level, and the
#   comment beside it names the 6-hour ceiling it protects against, cites the ~160-175 s the
#   job observably takes and the ~230 s it took while the docs gates ran in CI, says the 8 is
#   temporary, naming two issues whose landing did not bring the job back under it, and says
#   the budget assumes those gates stay out of CI.
#   .github/workflows/pages.yml, the `deploy` job: `timeout-minutes: 10` at job level, and
#   the comment beside it names the same 6-hour ceiling, cites the 11–23 s the job
#   observably takes, and says why its number is larger than the gates job's.
#   Every job in every workflow file declares a job-level `timeout-minutes`.
#   ci.yml's workflow-level `concurrency` cancels a PR's in-progress run on a newer push to
#   it, and never a push to main.
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

name="ci.yml gates: timeout-minutes 8, with a comment citing the 6-hour ceiling, the measured 160-175 s, ~230 s, the temporary raise, and docs gates staying out of CI"
problems=()

if timeout_comment "$CI_YML" gates 8; then
  probe_ceiling
  probe "comment does not cite the measured 160-175 s the job takes" \
    '(^|[^0-9])(1[5-9][0-9])[ -]?s'
  probe "comment does not say the 8 is temporary, naming what has to land first" \
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

timeouts_over() {
  local wf="$1" cap="$2" job minutes
  while IFS= read -r job; do
    [[ -n "$job" ]] || continue
    minutes="$(job_block "$wf" "$job" | sed -nE 's/^    timeout-minutes:[ ]*([0-9]+).*/\1/p')"
    [[ -n "$minutes" && "$minutes" -gt "$cap" ]] \
      && problems+=("${wf##*/}: job '$job' declares timeout-minutes $minutes, above $cap")
  done < <(job_names "$wf")
  return 0
}

name="a ci.yml job declaring timeout-minutes above 10 fails, named, and every job in ci.yml declares at most 10"
problems=()

fixture="$(scratch_dir)/ci.yml"
cat > "$fixture" <<'YML'
jobs:
  slow:
    runs-on: ubuntu-latest
    timeout-minutes: 11
  capped:
    runs-on: ubuntu-latest
    timeout-minutes: 10
YML
timeouts_over "$fixture" 10
expect_eq "$name (a fixture job at 11 is named, one at 10 is not)" \
  "ci.yml: job 'slow' declares timeout-minutes 11, above 10" "${problems[*]-}"
problems=()
timeouts_over "$CI_YML" 10
report "$name"

name="ci.yml gates: python from actions/setup-python at 3.12 with pip's cache keyed on requirements-dev.txt, make install-dev before make test, on ubuntu-latest with its timeout-minutes"
problems=()

gates="$(job_block "$CI_YML" gates)"
gates_has() {
  grep -E "$2" > /dev/null <<< "$gates" || problems+=("$1")
}
gates_has "gates job does not run on ubuntu-latest" \
  '^    runs-on:[ ]*ubuntu-latest[ ]*$'
gates_has "gates job declares no job-level timeout-minutes" \
  '^    timeout-minutes:[ ]*[0-9]+'
gates_has "gates job has no actions/setup-python step" \
  '^[ ]+(- )?uses:[ ]*actions/setup-python@'
gates_has "setup-python is not pinned to python-version 3.12" \
  "^[ ]+python-version:[ ]*[\"']?3\.12[\"']?[ ]*$"
gates_has "setup-python does not declare cache: pip" \
  "^[ ]+cache:[ ]*[\"']?pip[\"']?[ ]*$"
gates_has "pip's cache is not keyed on requirements-dev.txt" \
  "^[ ]+cache-dependency-path:[ ]*[\"']?requirements-dev\.txt[\"']?[ ]*$"
install_at="$(grep -m 1 -nE '^[ ]+run:[ ]*make install-dev[ ]*$' <<< "$gates" | cut -d: -f1)"
test_at="$(grep -m 1 -nE '^[ ]+run:[ ]*make test[ ]*$' <<< "$gates" | cut -d: -f1)"
if [[ -z "$install_at" ]]; then
  problems+=("gates job has no step running make install-dev")
elif [[ -z "$test_at" ]] || [[ "$install_at" -ge "$test_at" ]]; then
  problems+=("make install-dev does not run before make test (install at line ${install_at}, test at line ${test_at:-none})")
fi
report "$name"

name="ci.yml cancels a PR's in-progress run on a newer push to that PR, and never cancels a push to main"
problems=()
top="$(awk '/^jobs:[[:space:]]*$/ { exit } { print }' "$CI_YML")"
grep -E '^concurrency:[[:space:]]*$' > /dev/null <<< "$top" ||
  problems+=("ci.yml declares no workflow-level concurrency")
grep -E '^  group:.*github\.event\.pull_request\.number[[:space:]]*\|\|[[:space:]]*github\.ref' > /dev/null <<< "$top" ||
  problems+=("concurrency group is not keyed on the PR number, falling back to the ref")
grep -E "^  cancel-in-progress:[[:space:]]*\\$\\{\\{[[:space:]]*github\\.event_name[[:space:]]*==[[:space:]]*'pull_request'[[:space:]]*\\}\\}[[:space:]]*$" > /dev/null <<< "$top" ||
  problems+=("cancel-in-progress is not limited to pull_request events, so a push to main could be cancelled")
report "$name"

finish

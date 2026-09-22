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

# probe_ceiling — the one fact both comments owe, named once. Every other probe in this
# suite is specific to its job, but the 6-hour default is what both budgets exist to bound,
# so the two cases asserted it with the same message and the same regex; sharing them keeps
# the wording from drifting apart on one side only.
probe_ceiling() {
  probe "comment beside the timeout does not name the 6-hour default ceiling" \
    '(6[ -]?h|six[ -]?hour)'
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

# job_names <file> -> every job key that file defines, one per line.
# Only the keys under the top-level `jobs:` mapping count: indent 2 is also where
# `permissions:` and `concurrency:` put their own keys, so scanning the whole file for
# indent-2 keys would report `group` and `contents` as jobs. The block runs from `jobs:`
# to the next line that starts at column 0, the way job_block runs to the next indent-2
# line. This is what lets a case sweep the jobs that exist rather than name them.
job_names() {
  awk '
    /^jobs:[[:space:]]*$/ { inside = 1; next }
    inside && /^[^[:space:]]/ { exit }
    inside && /^  [A-Za-z0-9_.-]+:[[:space:]]*$/ {
      sub(/:[[:space:]]*$/, ""); sub(/^  /, ""); print
    }
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

# 2. The same shape for the other workflow: the `deploy` job in pages.yml caps at 10, and
#    its comment has to carry the three facts that make 10 the right number rather than a
#    copy of the gates job's 3 — the ceiling it protects against, the duration it leaves
#    headroom over, and why this job's budget is the larger one.
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

# 3. The two cases above pin the two jobs that exist today, by name. This one is for the
#    job that does not exist yet: it enumerates every job in every workflow file and asks
#    only that each declares a job-level timeout-minutes, whatever the number and whatever
#    the comment. A job added later without one inherits the same 6-hour ceiling, and the
#    named cases would stay green the whole time it did.
#    The sweep also has to fail when it reads nothing — no workflow files, or a file whose
#    jobs it could not enumerate — because a sweep that found no jobs would otherwise
#    report "every job declares one" as a pass.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

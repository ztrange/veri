#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a conductor to do with the run's hard
# timeout, read as text.
#
# Contract under test:
#   SKILL.md's preflight section times the green-baseline run it already does, hands that
#   measurement to `leaf-timeout.sh`, and exports the result as `VERI_TIMEOUT` so every
#   leaf of the run is launched under it.
#   SKILL.md's plan-comment step says that comment states the timeout and the baseline it
#   was derived from.
#
# Run: scripts/tests/skill-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"


source "$HERE/lib/harness.sh"

section() {
  want="$1" awk '
    $0 ~ ENVIRON["want"] { inside = 1; print; next }
    inside && /^### / { exit }
    inside' "$ROOT/$skill_md"
}

paragraphs() {
  awk '/^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | tr '[:upper:]' '[:lower:]'
}

records_of() {
  records_from="$skill_md $1"
  records="$(section "$2" | paragraphs)"
  [[ -n "$records" ]] && return 0
  problems+=("$3")
  return 1
}

claim() {
  local what="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$records"
  problems+=("$records_from: no step $what")
}

elapsed_re='(^|[^a-z])(time|timed|times|timing|elapsed|wall|duration|sec)([^a-z-]|$)'

preflight_records() {
  records_of preflight '^### [0-9]+\..*[Pp]reflight' \
    "$skill_md has no numbered '### … Preflight' section — what preflight does with the timeout could not be read"
}
plan_records() {
  records_of plan '^### [0-9]+\..*[Pp]lan' \
    "$skill_md has no numbered '### … plan' section — what the plan comment states could not be read"
}

claim_exports_timeout() {
  claim 'exports the result as VERI_TIMEOUT so every leaf of the run is launched under it' \
    'veri_timeout' 'export|every leaf|each leaf|all leaves|every launch|rest of the run'
}

name="$skill_md's preflight times the baseline run, derives the timeout with leaf-timeout.sh and exports it as VERI_TIMEOUT for every leaf, and the plan comment states it with the baseline it came from"
problems=()

if preflight_records
then
  claim 'times the green-baseline run it already does' \
    'baseline' "$elapsed_re"
  claim 'hands that measurement to leaf-timeout.sh' \
    'leaf-timeout\.sh' "$elapsed_re|baseline"
  claim_exports_timeout
fi

if plan_records
then
  claim 'has the plan comment state the timeout and the baseline it was derived from' \
    'timeout' 'baseline' 'comment'
fi
report "$name"

name="$skill_md's preflight times the full tier, hands that measurement to leaf-timeout.sh and exports it as VERI_TIMEOUT for every leaf, and the plan comment names the tier the number came from"
problems=()

full_re='(^|[^a-z])full(-[a-z]+)?([^a-z-]|$)'

if preflight_records
then
  claim 'times a full-tier run, the work a leaf actually does' \
    "$full_re" "$elapsed_re"
  claim 'hands the full-tier measurement to leaf-timeout.sh' \
    'leaf-timeout\.sh' "$full_re"
  claim_exports_timeout
fi

if plan_records
then
  claim 'has the plan comment name the tier the timeout was derived from' \
    'timeout' 'comment' "$full_re|tier"
fi
report "$name"

name="#954: $skill_md's preflight step 7 names the run-state file the settled timeout is recorded in and says supervise.sh reads it when VERI_TIMEOUT is unset, not that an export in the conductor's shell is in force for later launches"
problems=()

if preflight_records
then
  claim 'names .tdd/issue-<n>-timeout as where the settled timeout is recorded and says supervise.sh reads it when VERI_TIMEOUT is unset' \
    'leaf-timeout\.sh' '\.tdd/issue-<n>-timeout' 'supervise\.sh' 'veri_timeout[^.]*unset'
  if grep -E "conductor's own shell" <<< "$records" | grep -E 'in force' > /dev/null
  then
    problems+=("$records_from: still claims an export in the conductor's own shell is in force for later launches")
  fi
fi
report "$name"

name="#954: $skill_md makes the leaf-timeout.sh call that records .tdd/issue-<n>-timeout after step 1.2 has entered the issue's worktree, not from the caller's checkout where preflight runs"
problems=()

entered="$(grep -m 1 -nE 'issue-worktree\.sh <n> .*cd "\$wt"' "$ROOT/$skill_md" | cut -d: -f1)"
recording="$(grep -nE 'VERI_ISSUE=<n>.*leaf-timeout\.sh' "$ROOT/$skill_md" | cut -d: -f1)"
if [[ -z "$entered" ]]
then
  problems+=("$skill_md: no step 1.2 line that enters the worktree with issue-worktree.sh")
elif [[ -z "$recording" ]]
then
  problems+=("$skill_md: no leaf-timeout.sh call carrying VERI_ISSUE=<n>, the one that records the settled timeout")
else
  for line in $recording
  do
    (( line > entered )) ||
      problems+=("$skill_md:$line: the leaf-timeout.sh call that records the settled timeout runs before step 1.2 enters the worktree (line $entered)")
  done
fi
report "$name"

name="#1037: section given '^### run\\.sh' starts at '### run.sh', not at '### runXsh'"
fixture="$(scratch_dir)"
printf '### runXsh\nwrong\n### run.sh\nright\n### end\n' > "$fixture/SKILL.md"
expect_eq "$name" $'### run.sh\nright' "$(ROOT="$fixture" skill_md=SKILL.md section '^### run\.sh')"

finish

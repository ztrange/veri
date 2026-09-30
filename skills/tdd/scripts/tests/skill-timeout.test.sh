#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a conductor to do with the run's hard
# timeout. Like skill-identity.test.sh and workflow-timeouts.test.sh this suite belongs to
# no single script: its subject is the procedure, read as text, the way the session that
# follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-identity.test.sh.
#
# Why this exists (issue #121): `leaf-timeout.sh` derives the timeout, but a script nobody
# calls changes nothing. The derivation lives in the conductor's own procedure — there is
# no leaf and no script that could carry it, because the measurement it needs is taken by
# preflight and the value it produces has to be in the environment before the first leaf
# launches. On #71 that value was the fixed 900 s against a 140-250 s suite, and two leaves
# were killed as stuck while working; what fixes it is this document saying so.
#
# Contract under test (this step only):
#   SKILL.md's preflight section times the green-baseline run it already does, hands that
#   measurement to `leaf-timeout.sh`, and exports the result as `VERI_TIMEOUT` so every
#   leaf of the run is launched under it.
#   SKILL.md's plan-comment step says that comment states the timeout and the baseline it
#   was derived from, so a human reading the issue thread can see which number the run is
#   using and why — the fact that had to be reconstructed from bail timestamps on #71.
#
# Run: scripts/tests/skill-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"

pass=0 fail=0

source "$HERE/lib/harness.sh"

section() {
  awk -v want="$1" '
    $0 ~ want { inside = 1; print; next }
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

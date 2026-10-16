#!/usr/bin/env bash
# Unit test for where skills/tdd/SKILL.md verifies the plan, read as text.
#
# Contract under test — four cases, one per criterion:
#   1. SKILL.md launches the `plan` verdict between the instruction that commits the ledger
#      and the heading that opens the cycle loop, and the prose in that same span says a
#      REJECT rewrites the plan and re-verifies it, rather than ending the run.
#   2. The same span sends the third outcome — exit 2, no verdict rendered at all — down the
#      **system** failure bail, rather than letting it read as a PASS.
#   3. The script inventory's own entries for `build-verify-prompt.sh`, `verify.sh` and
#      `run-verdict.sh` name `plan` among the phases they accept.
#   4. One paragraph of the "2. Scope & plan" section orders a step that brings in code (a
#      port, a new module) after the steps pinning its branches, or has it bring in only the
#      branches its own test requires.
#
# Run: skills/tdd/scripts/tests/skill-plan-verify.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

commit_re='git commit -m "plan: scope'
loop_re='^### 3[.] The cycle loop'
plan_launch_re='(run-verdict|verify)[.]sh.* plan '
exit2_re='[(]exit 2[)]'


source "$HERE/lib/harness.sh"

line_of() {
  awk -v re="$1" 'n == 0 && match($0, re) { n = NR } END { print n + 0 }' "$skill_path"
}

span_text() {
  awk -v a="$1" -v b="$2" 'NR > a && NR < b' "$skill_path" |
    tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

line_in_span() {
  awk -v a="$1" -v b="$2" -v re="$3" \
    'n == 0 && NR > a && NR < b && match($0, re) { n = NR } END { print n + 0 }' "$skill_path"
}

bullet_text() {
  awk -v a="$1" -v b="$2" -v re="$3" '
    NR <= a || NR >= b { next }
    !inb && match($0, re) { inb = 1; print; next }
    inb && ($0 ~ /^[[:space:]]*$/ || $0 ~ /^- /) { inb = 0 }
    inb { print }
  ' "$skill_path" | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

finish

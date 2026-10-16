#!/usr/bin/env bash
# Unit tests for when the conductor ticks an acceptance criterion in the issue body, as
# skills/tdd/SKILL.md prescribes it, read as text.
#
# Contract under test:
#   1. In both SKILL.md's cycle loop and its pin path, the instruction that runs
#      `tick-issue-criterion.sh` also runs `criterion-finished.sh`, ticks on its exit 0 and
#      ticks nothing on its exit 3; the cycle loop's instruction still posts `### ✅ Step done`.
#   2. SKILL.md step 2's plan-writing guidance tells the conductor to end each ledger step with
#      ` ⟦criterion k⟧` for the criterion it serves, and to leave a gap step without one.
#
# Run: scripts/tests/skill-criterion-finished.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/first-record.sh"

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

section_records() {
  awk -v head="$1" '
    $0 == head { inside = 1; level = index(head, " "); next }
    inside && /^#+ / && index($0, " ") <= level { exit }
    inside' "$skill_path" | records_of
}

finish

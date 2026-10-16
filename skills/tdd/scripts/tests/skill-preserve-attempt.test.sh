#!/usr/bin/env bash
# Unit tests for the conductor's own preservation of a troubled step's attempt, as
# skills/tdd/SKILL.md prescribes it, read as text.
#
# Contract under test:
#   SKILL.md prescribes a `$S/preserve-attempt.sh` call in the Bailing procedure, ahead of
#   that procedure's `git reset --hard HEAD`; and beside every `event.sh prediction-diverged`
#   mark it prescribes.
#
# Run: scripts/tests/skill-preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"


source "$HERE/lib/harness.sh"

instructions() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

preserve_re='\$s/preserve-attempt\.sh'

bail_section() {
  awk 'BEGIN { inside = 0 }
    /^## / { inside = ($0 == "## Bailing") ; next }
    inside { print NR ": " $0 }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

finish

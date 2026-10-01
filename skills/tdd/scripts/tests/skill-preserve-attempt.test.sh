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

name="$skill_md preserves the attempt on a bail, before the bail's reset, and beside every prediction-diverged mark"
problems=()

section="$(bail_section)"
if [[ -z "$section" ]]; then
  problems+=("$skill_md has no \`## Bailing\` section to read — the bail's preservation could not be checked")
else
  preserve_line="$(grep -m1 -E "$preserve_re" <<< "$section" | cut -d: -f1)"
  reset_line="$(grep -m1 -E 'git reset --hard head' <<< "$section" | cut -d: -f1)"
  if [[ -z "$preserve_line" ]]; then
    problems+=("$skill_md's Bailing section prescribes no \`\$S/preserve-attempt.sh\` call — a bail keeps its leaf's tree nowhere, and the three leaf-side marks preserve one")
  elif [[ -z "$reset_line" ]]; then
    problems+=("$skill_md's Bailing section no longer prescribes \`git reset --hard HEAD\` — what the preservation must come ahead of could not be read")
  elif [[ "$preserve_line" -gt "$reset_line" ]]; then
    problems+=("$skill_md bails by preserving at line $preserve_line, after the \`git reset --hard HEAD\` at line $reset_line — the reset empties the tree the snapshot would have kept")
  fi
fi

records="$(instructions)"
if [[ -z "$records" ]]; then
  problems+=("$skill_md has no instructions to read — the prediction-diverged preservation could not be checked")
else
  marks=0
  while IFS= read -r line; do
    [[ "$line" =~ event\.sh[[:space:]]+prediction-diverged([^a-z0-9-]|$) ]] || continue
    marks=$((marks + 1))
    [[ "$line" =~ $preserve_re ]] ||
      problems+=("$skill_md marks a prediction-diverged attempt with no \`\$S/preserve-attempt.sh\` beside it: $(printf '%.130s' "$line")")
  done <<< "$records"
  [[ "$marks" -gt 0 ]] ||
    problems+=("$skill_md prescribes no \`event.sh prediction-diverged\` call — where its preservation belongs could not be read")
fi
report "$name"

finish

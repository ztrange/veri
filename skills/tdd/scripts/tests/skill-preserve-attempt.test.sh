#!/usr/bin/env bash
# Unit tests for the conductor's own preservation of a troubled step's attempt — like
# skill-event-marks.test.sh this suite belongs to no single script: its subject is
# skills/tdd/SKILL.md, read as text, the way the session that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-event-marks.test.sh.
#
# Why this exists (issue #409): five marks make a step one whose evidence a reader will
# want — reject, no-verdict, stuck, bail, prediction-diverged — and three of them are
# written from inside a script, so `preserve_attempt` is called there by construction
# (verify.sh on a REJECT or a malformed verdict, supervise.sh on a killed-stuck leaf).
# The other two are the conductor's, and the conductor is prose: a bail and a
# prediction-diverged mark preserve nothing unless this document tells the session to.
#
# The bail half is not just "somewhere in the section" either. A bail's first step is
# `git reset --hard HEAD`, which throws the half-done step's tree away — so a preservation
# prescribed after it snapshots a tree the reset already emptied, which is a preservation
# that reads right and keeps nothing. The order is the behaviour here, so the case asks it.
#
# Contract under test (this step only):
#   SKILL.md prescribes a `$S/preserve-attempt.sh` call in the Bailing procedure, ahead of
#   that procedure's `git reset --hard HEAD`; and beside every `event.sh prediction-diverged`
#   mark it prescribes.
#
# Run: scripts/tests/skill-preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"

pass=0 fail=0

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

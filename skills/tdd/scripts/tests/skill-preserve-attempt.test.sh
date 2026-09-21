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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which of the two marks is uncovered rather than just that one is.
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

# instructions — the document's numbered steps, bullets and paragraphs, one per line and
# lowercased, exactly as skill-event-marks.test.sh reads them. Joining a record onto one
# line is what lets the prediction-diverged probe ask whether ONE instruction carries both
# halves — the mark and the preservation — rather than two sentences in different sections
# that happen to share a word.
instructions() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

# preserve_re — how this document spells a call to `preserve-attempt.sh`, as a regex over a
# lowercased record or line: the call, not a mention. Every script the document orders run is
# written `$S/<script>`, so the `$S/` prefix is what tells a prescribed call from prose about
# one. Both probes ask it, so the spelling is one decision rather than two.
preserve_re='\$s/preserve-attempt\.sh'

# bail_section — the `## Bailing` section's lines, each prefixed with its line number in the
# document and lowercased. Bounded by the next `## ` heading: the Resume section that follows
# resets the worktree too, and a preservation prescribed there is not one a bail performs.
bail_section() {
  awk 'BEGIN { inside = 0 }
    /^## / { inside = ($0 == "## Bailing") ; next }
    inside { print NR ": " $0 }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

# 1. The whole of this step's criterion, as one case: the two conductor-side marks, each
#    preserving the attempt the way the three leaf-side ones already do. They are one case
#    because they are one wiring — the point of the issue is that a troubled step keeps its
#    evidence, and a run that keeps it on three of the five marks keeps it on none of the
#    runs that ended the other two ways.
name="$skill_md preserves the attempt on a bail, before the bail's reset, and beside every prediction-diverged mark"
problems=()

# The bail half. Two line numbers out of the section: the first prescribed preservation, and
# the reset that would otherwise have thrown the tree away first.
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

# The prediction-diverged half. Every record that writes the mark, because the document
# prescribes it twice — once in Red and once in the revise loop — and a preservation added to
# only one of them leaves whichever branch a run actually took uncovered half the time.
records="$(instructions)"
if [[ -z "$records" ]]; then
  problems+=("$skill_md has no instructions to read — the prediction-diverged preservation could not be checked")
else
  marks=0
  while IFS= read -r line; do
    # Bounded on the right so a longer mark name this document may grow later cannot answer
    # for this one, the way skill-event-marks.test.sh bounds its own event names.
    [[ "$line" =~ event\.sh[[:space:]]+prediction-diverged([^a-z0-9-]|$) ]] || continue
    marks=$((marks + 1))
    [[ "$line" =~ $preserve_re ]] ||
      problems+=("$skill_md marks a prediction-diverged attempt with no \`\$S/preserve-attempt.sh\` beside it: $(printf '%.130s' "$line")")
  done <<< "$records"
  # Fail closed: no mark prescribed anywhere means the loop asked nothing, which must not
  # read as a pass.
  [[ "$marks" -gt 0 ]] ||
    problems+=("$skill_md prescribes no \`event.sh prediction-diverged\` call — where its preservation belongs could not be read")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

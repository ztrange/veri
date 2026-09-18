#!/usr/bin/env bash
# Unit tests for what the conductor narrates out of the red leaf's prediction — like
# skill-event-marks.test.sh and skill-suite-runs.test.sh this suite belongs to no single
# script: its subject is skills/tdd/SKILL.md, read as text, the way the session that
# follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-suite-runs.test.sh.
#
# Why this exists (issue #193): the red leaf now states, before it runs anything, which
# assertion it expects to fire and on what values, and reports that back as
# `PREDICTED_FAILURE:` with a `PREDICTION: MATCHED | DIVERGED` beside it. The prediction is
# developer rationale, so it must never reach a verifier — verify-red establishes ground
# truth by running the test itself, and a verifier told what the developer expected is a
# verifier primed to agree. The one place it belongs is the issue thread: a human reading
# the `### 🔴 Red` comment sees what the test was expected to do beside what it did, and on
# a repository where the two keep diverging that thread is the evidence. A report line
# nobody narrates is data the run collected and threw away.
#
# Contract under test (this step only):
#   SKILL.md's Red phase tells the conductor to put both halves in the `### 🔴 Red` comment
#   — the predicted failure, and whether the observed one matched it. Any wording that
#   carries the two facts passes; how the section phrases them is the writer's.
#
# Run: scripts/tests/skill-red-prediction.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path
# resolved for the probes to read, so a message can never name a file the probes did not
# open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

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

# plain — stdin with emphasis marks and backticks dropped and the case folded, because
# `**PREDICTION: MATCHED**` and "prediction: matched" are the same sentence. The probes'
# regexes are then written one way and match however the author chose to mark the words up.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# doc_text <heading-prefix> <from-regex> — the text of the first SKILL.md section whose
# heading STARTS WITH the literal <heading-prefix>, from the first line matching
# <from-regex>, up to the line before the next heading of any level. Anchoring at the
# narrate sub-step is what keeps this case about the comment: the word "prediction" three
# sub-steps above, where the leaf's report is read, is not an instruction to narrate it.
# The text is normalised through `plain` and joined onto one line, so a sentence split over
# a line break still reads as one.
doc_text() {
  awk -v h="$1" -v from="$2" '
    !in_s && index($0, h) == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$skill_path" | plain | tr '\n' ' '
}

# says <regex> <fact> — one thing the narration text has to carry, written as the regex of
# any wording that would carry it; `fact` names it once if nothing matches.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

# 1. One criterion — the Red comment carries the prediction and whether it matched — and so
#    one case: a thread showing only one of the two halves cannot be read for divergence,
#    and the fix to either is one edit to one instruction.
name="$skill_md's Red narration puts the leaf's prediction and whether it matched in the \`### 🔴 Red\` comment"
problems=()
# The narrate sub-step: the one that posts the comment, found by the heading it posts
# rather than by its number, which a reordering would move.
text="$(doc_text '#### Red' '### 🔴 Red')"
if [[ "$text" != *[!\ ]* ]]; then
  # Fail closed: no narrate sub-step means the section was renamed or the comment moved,
  # and neither probe below ran — which must not read as two passes.
  problems+=("$skill_md's Red section has no instruction posting the \`### 🔴 Red\` comment — what that comment carries could not be read")
else
  says 'predicted_failure|predicted failure|prediction it (made|wrote)|what it predicted' \
    "$skill_md tells the conductor to post the \`### 🔴 Red\` comment without the leaf's predicted failure, so the thread shows what the test did with nothing to read it against"
  says 'prediction: *matched|matched \| diverged|whether (the|its) (prediction|predicted failure) (matched|was)|matched or diverged' \
    "$skill_md's \`### 🔴 Red\` comment never says whether the prediction matched, so a divergence the leaf reported is narrated as an ordinary red"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

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
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

doc_text() {
  awk -v h="$1" -v from="$2" '
    !in_s && index($0, h) == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$skill_path" | plain | tr '\n' ' '
}

section() {
  text="$(doc_text "$1" "$2")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$3")
  return 1
}

red_section()    { section '#### Red' "$@"; }
revise_section() { section '## Revising on a REJECT' "$@"; }

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

exit_0_or_2='exit(s| code)? 0 (or|\|) 2|0 or 2|\b0\b[^.]*\b2\b'

name="$skill_md's Red narration puts the leaf's prediction and whether it matched in the \`### 🔴 Red\` comment"
problems=()
if red_section '### 🔴 Red' \
  "$skill_md's Red section has no instruction posting the \`### 🔴 Red\` comment — what that comment carries could not be read"; then
  says 'predicted_failure|predicted failure|prediction it (made|wrote)|what it predicted' \
    "$skill_md tells the conductor to post the \`### 🔴 Red\` comment without the leaf's predicted failure, so the thread shows what the test did with nothing to read it against"
  says 'prediction: *matched|matched \| diverged|whether (the|its) (prediction|predicted failure) (matched|was)|matched or diverged' \
    "$skill_md's \`### 🔴 Red\` comment never says whether the prediction matched, so a divergence the leaf reported is narrated as an ordinary red"
fi
report "$name"

name="$skill_md's Red section runs red-divergence.sh and sends a diverged prediction to the red revise loop"
problems=()
if red_section 'red-divergence' \
  "$skill_md's Red section never runs \`red-divergence.sh\` on the leaf's report, so a \`PREDICTION: DIVERGED\` goes to verify-red like a matched one"; then
  says "$exit_0_or_2" \
    "$skill_md names \`red-divergence.sh\` without saying which of its exit codes takes the diverged path, so exit 2 — a prediction nobody can read — is not handled like a divergence"
  says 'skips? verify-red and verify-pin|skips? both verify-red and verify-pin|verify-red and verify-pin entirely' \
    "$skill_md does not tell the conductor to skip verify-red and verify-pin on a divergence, so the blind verifier still judges a test the developer already flagged as suspect"
  says 'verify-red.reason' \
    "$skill_md does not tell the conductor to write the divergence reason to \`.tdd/verify-red.reason\`, so the revise leaf is launched with nothing to answer"
  says 'prediction-diverged' \
    "$skill_md does not tell the conductor to emit a \`prediction-diverged\` event, so a divergence leaves no mark in the run log"
  says 'revise loop|revising on a reject|revise' \
    "$skill_md does not send a diverged red into the revise loop, so the step continues as though the test were sound"
fi
report "$name"

name="$skill_md's revise loop checks a revise-red report with red-divergence.sh and spends the attempt without re-verifying"
problems=()
if revise_section 'red-divergence' \
  "$skill_md's \`Revising on a REJECT\` section never runs \`red-divergence.sh\` on a revise-red report, so a rewritten red test that failed for the wrong reason goes straight back to the blind verifier"; then
  says 'revise-red|revise of red|red revise|phase is red|<phase> is red' \
    "$skill_md does not say the check is the red phase's, so the loop runs it on a green or refactor revise report, whose own template writes no \`PREDICTION:\` line"
  says "$exit_0_or_2" \
    "$skill_md names \`red-divergence.sh\` in the revise loop without saying which of its exit codes takes the diverged path, so exit 2 — a prediction nobody can read — is not handled like a divergence"
  says 'without (launching|running|re-running) the verifier|skip(s|ping)? (the )?re-verif|do not re-verify|never re-verif|without re-verifying' \
    "$skill_md does not tell the conductor to skip the re-verification on a diverged revise-red, so the blind verifier judges a test the revise leaf itself flagged as suspect"
  says 'spends? (the |that )?(next )?attempt|attempt .* (is |still )?spen|counts? against|against .*revise_budget' \
    "$skill_md does not say the diverged attempt still spends \`REVISE_BUDGET\`, so a red test that keeps diverging loops forever instead of bailing the step"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

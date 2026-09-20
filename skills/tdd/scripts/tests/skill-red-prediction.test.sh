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

# section <heading-prefix> <from-regex> <missing-message> — set `text` to that section's words
# from <from-regex> on, and say whether a case's probes can run at all. Nothing matching means
# the anchor is gone — the section was renamed, or the instruction moved — so the message goes
# into `problems` and 1 comes back: a case whose anchor vanished must read as one failure, never
# as a row of passes over an empty string.
section() {
  text="$(doc_text "$1" "$2")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$3")
  return 1
}

# The two sections the cases below anchor in, each heading written once so a rename to either is
# one edit here rather than one per case: `#### Red` holds the Red phase's own instructions, and
# `## Revising on a REJECT` the revise loop that owes the same check a second time.
red_section()    { section '#### Red' "$@"; }
revise_section() { section '## Revising on a REJECT' "$@"; }

# says <regex> <fact> — one thing the narration text has to carry, written as the regex of
# any wording that would carry it; `fact` names it once if nothing matches.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

# The one probe both divergence cases owe: any wording naming exit 0 and exit 2 together as the
# codes that take the diverged path. Written once because the Red section and the revise loop
# each have to say it, and a regex copied into two cases is one chance for a rewording to be
# pinned in only one of them. The failure messages stay per-case: each names its own section.
exit_0_or_2='exit(s| code)? 0 (or|\|) 2|0 or 2|\b0\b[^.]*\b2\b'

# 1. One criterion — the Red comment carries the prediction and whether it matched — and so
#    one case: a thread showing only one of the two halves cannot be read for divergence,
#    and the fix to either is one edit to one instruction.
name="$skill_md's Red narration puts the leaf's prediction and whether it matched in the \`### 🔴 Red\` comment"
problems=()
# The narrate sub-step: the one that posts the comment, found by the heading it posts
# rather than by its number, which a reordering would move.
if red_section '### 🔴 Red' \
  "$skill_md's Red section has no instruction posting the \`### 🔴 Red\` comment — what that comment carries could not be read"; then
  says 'predicted_failure|predicted failure|prediction it (made|wrote)|what it predicted' \
    "$skill_md tells the conductor to post the \`### 🔴 Red\` comment without the leaf's predicted failure, so the thread shows what the test did with nothing to read it against"
  says 'prediction: *matched|matched \| diverged|whether (the|its) (prediction|predicted failure) (matched|was)|matched or diverged' \
    "$skill_md's \`### 🔴 Red\` comment never says whether the prediction matched, so a divergence the leaf reported is narrated as an ordinary red"
fi
report "$name"

# 2. The other half of the same report line (#356): a DIVERGED prediction is the conductor's
#    gate, not a verifier's — verify-red is blind and the prediction is the developer's
#    reasoning, so nothing downstream can act on it. One criterion, one case: the Red
#    section has to run `red-divergence.sh` on the leaf's report and, when it answers 0
#    (diverged) or 2 (no prediction anyone can read), take the step down the revise path
#    instead of the verify one. All five facts are one instruction, so one case reads them.
name="$skill_md's Red section runs red-divergence.sh and sends a diverged prediction to the red revise loop"
problems=()
# Anchored at the first line naming the script, so the case reads the divergence
# instruction itself rather than the verify-red prose three sub-steps above, which already
# speaks of `.tdd/verify-red.reason` and of a revise loop.
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

# 3. The second hole the same report line opens (#356): a revise leaf rewrites the red test
#    and reports its own `PREDICTION:`, so the revise loop owes the same check the Red
#    section does before it re-verifies. One criterion, one case: the loop has to run
#    `red-divergence.sh` on a revise-red report and, on exit 0 or 2, spend the attempt
#    without launching the verifier at all.
name="$skill_md's revise loop checks a revise-red report with red-divergence.sh and spends the attempt without re-verifying"
problems=()
# Anchored at the first line naming the script inside the revise loop, so the case reads the
# loop's own check rather than the Red section's, which sits above it and already names both
# the script and its exit codes.
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

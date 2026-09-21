#!/usr/bin/env bash
# Unit tests for what the conductor does when a step's revise budget runs out — like
# skill-green-split.test.sh and skill-red-untestable.test.sh this suite belongs to no single
# script: its subject is skills/tdd/SKILL.md, read as text, the way the session that follows
# it reads it. Zero-dependency plain-shell asserts, same idiom, picked up by `make test`'s
# glob by existing.
#
# Why this exists (issue #408): exhausting `REVISE_BUDGET` goes straight to a
# `revise-exhausted` bail today, and the step's work is lost — although a step no blind
# verifier can be satisfied about in two attempts is usually a step carrying more than one
# behaviour, the very condition `SPLIT:` exists for. build-develop-prompt.sh now renders an
# `exhausted` phase and exhausted-outcome.sh resolves that leaf's report to one of three
# answers (exit 0 split · 1 needs the user · 3 neither). This suite pins the branch in
# SKILL.md that launches that leaf and acts on those three answers.
#
# Run: scripts/tests/skill-revise-exhausted.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path resolved
# for the probes to read, so a message can never name a file the probes did not open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# plain — stdin with emphasis marks and backticks dropped, the case folded and the lines
# joined onto one, because `SPLIT:` and **split** are the same word and a claim that wraps
# across two lines is still one claim.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# The heading the section is found by, spelled once: the probes look for it and the
# fail-closed message names it.
revise_heading='## Revising on a REJECT'

# revise_section — the lines after that heading, up to the next heading of any level,
# normalised through `plain`.
revise_section() {
  awk -v h="$revise_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain
}
section="$(revise_section)"

# unreadable — empty unless the section could not be read at all, in which case it is the
# half of the failure message the case would otherwise have to invent. Fail closed rather
# than probing an empty string, which would let "the section is gone" read as "it is right".
unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$revise_heading' section to read —"

# win <extended-regex> — the section text within 250 characters either side of the first
# match, or the empty string when there is none: the text a reader meets while working out
# what to do about that answer. 250 rather than a rounder, larger number because BSD grep —
# the one on the development machine this repository holds itself portable to — refuses an
# interval whose bound is over 255.
win() {
  grep -oE ".{0,250}$1.{0,250}" <<<"$section" | head -1
}

name="$skill_md's exhausted-budget branch launches the exhausted leaf and acts on exhausted-outcome.sh's three answers: replace the step on a split, park it on needs-user, bail revise-exhausted on neither"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does when a step's revise budget runs out could not be established")
else
  # 1. The leaf. Without it the last REJECT goes straight to the bail it does today and
  #    nothing ever asks the leaf which of the two conditions the step is in.
  grep -qE '\$s/build-develop-prompt\.sh exhausted' <<<"$section" ||
    problems+=("$skill_md's revise section never builds an exhausted-phase prompt, so a step whose budget ran out is bailed without anything asking whether it should have been split")

  # 2. The reader. The leaf answers in free-form prose around its report lines, and
  #    exhausted-outcome.sh is what resolves that to one of the three outcomes — a
  #    conductor reading the report itself makes the branch a judgement per run.
  if ! grep -qE '\$s/exhausted-outcome\.sh' <<<"$section"; then
    problems+=("$skill_md's revise section never runs exhausted-outcome.sh on the exhausted leaf's report, so which of the three outcomes it reported is decided by reading rather than by exit code")
  else
    outcome="$(win '\$s/exhausted-outcome\.sh')"
    grep -qE 'exit 0|exits? 0' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 0 is the split, so the conductor cannot tell the split answer from the other two")
    grep -qE 'exit 1|exits? 1' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 1 is the needs-user answer, so a step the leaf escalated is acted on as something else")
    grep -qE 'exit 3|exits? 3' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 3 is neither answer, so the outcome that must bail exactly as today has no branch of its own")
  fi

  # 3. The split branch: the criteria the leaf named take the place of the step that could
  #    not be satisfied — `instead-of`, not `before`, because the step itself is what was
  #    wrong — and the run carries on from the first of them.
  if ! grep -qE '\$s/add-ledger-step\.sh' <<<"$section"; then
    problems+=("$skill_md's revise section never runs add-ledger-step.sh on a split at exhaustion, so the criteria the leaf named are narrated and the plan the run reads is unchanged")
  else
    added="$(win '\$s/add-ledger-step\.sh')"
    grep -qE 'instead-of' <<<"$added" ||
      problems+=("$skill_md's revise section grows the ledger at exhaustion with a placement other than instead-of, so the step nothing could satisfy stays in the plan alongside the criteria that replaced it")
    grep -qE 'commit' <<<"$added" ||
      problems+=("$skill_md's revise section grows the ledger at exhaustion without committing it, so the replacement steps are lost the moment the run is resumed from the committed ledger")
    grep -qE 'next-unchecked' <<<"$section" ||
      problems+=("$skill_md's revise section never returns to next-unchecked.sh after replacing the step, so the run does not continue from the first of the criteria it just filed")
  fi

  # 4. The needs-user branch: a leaf that says the step needs a decision the run has no
  #    authority to make is answered by parking the step, not by bailing it as a
  #    methodology failure.
  if ! grep -qE 'needs_user|needs-user|needs the user' <<<"$section"; then
    problems+=("$skill_md's revise section never names the needs-user answer, so a leaf that escalates a step to the user is treated as one that volunteered nothing")
  else
    parked="$(win 'needs_user|needs-user|needs the user')"
    grep -qE 'park' <<<"$parked" ||
      problems+=("$skill_md's revise section names the needs-user answer without parking the step on it, so an escalation the leaf made deliberately ends as the same bail as saying nothing")
  fi

  # 5. And the third outcome, unchanged: neither answer is still the bail the section does
  #    today, with the same cause token a human's classification is read from.
  if ! grep -qE 'revise-exhausted' <<<"$section"; then
    problems+=("$skill_md's revise section no longer names the revise-exhausted cause, so a leaf that volunteered neither answer leaves the conductor to invent a stop for a step it already had one for")
  else
    bailed="$(win 'revise-exhausted')"
    grep -qE 'bail' <<<"$bailed" ||
      problems+=("$skill_md's revise section names revise-exhausted without bailing on it, so the outcome that should end the step exactly as today carries on instead")
  fi
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

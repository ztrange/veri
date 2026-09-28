#!/usr/bin/env bash
# Unit test for what the two prose documents say about which leaves run the full test
# suite: skills/tdd/SKILL.md where it describes each phase's leaf, and the repository's own
# CLAUDE.md where it describes suite runs. Like skill-test-command.test.sh and
# docs-gap-adr.test.sh this suite has no script as its subject — it reads documents as text,
# in the same zero-dependency plain-shell idiom, and is picked up by `make test`'s glob by
# existing.
#
# Why this exists (issue #144): the developer prompts changed under the leaf-cost thread.
# The red leaf now runs the suite that holds its new case, the refactor leaf the suites
# covering the files it touched, and the full suite runs where the guarantee lives — once in
# develop-green before it reports, and in the two blind verifiers. SKILL.md still tells the
# conductor that the refactor leaf "runs the full suite", and CLAUDE.md still says `make
# test` "is what every veri leaf runs after every edit". A conductor reading the stale
# sentence budgets the wrong run time, and the next agent reading CLAUDE.md re-derives the
# old rule and puts it back; prose that contradicts the prompts is worse than prose that
# says nothing, because it is the account a human trusts.
#
# Contract under test:
#   SKILL.md's Red phase says its leaf runs the suite holding the new case; its Green phase
#   says its leaf runs the full suite; its Refactor loop says the transform leaf runs the
#   suites covering the touched files and that the full suite runs at verify-refactor.
#   CLAUDE.md names which leaves run the full suite, and no longer claims every leaf runs it
#   after every edit.
# Each probe accepts any wording that carries its fact — what these documents say is pinned,
# how they phrase it is the writer's.
#
# Run: scripts/tests/skill-suite-runs.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# Each document twice: the path as every failure message spells it, and the same path
# resolved for the probes to read. One constant for both, so a message can never name a file
# the probes did not open. Two documents, so each resolved path is named after its own — a
# bare `md` would not say which, and `cmd` in this repository is the test command.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

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
# `**full suite**` and "full suite" are the same sentence. Both readers below normalise
# through this, so a probe's regex is written one way and matches either document however
# its author chose to mark the words up.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# doc_text <file> <heading-prefix> <from-regex> — the text of the first section of <file>
# whose heading STARTS WITH the literal <heading-prefix>, up to the line before the next
# heading of any level; from the first line matching <from-regex> when one is given, so a
# claim about one sub-step is not answered by a sentence three sub-steps above it. The text
# is normalised through `plain` and its lines are then joined onto one, so a claim split
# over a line break still reads as one sentence.
#
# A literal prefix rather than a regex: the phase headings carry trailing prose after an em
# dash, so the prefix is what identifies them, and a literal is what lets `need_text` below
# quote the same string it searched for.
doc_text() {
  awk -v h="$2" -v from="$3" '
    !in_s && index($0, h) == 1 { in_s = 1; want = (from == "" ? 1 : 0); next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$1" | plain | tr '\n' ' '
}

# need_text <heading-prefix> [from-regex] — the SKILL.md section under <heading-prefix> into
# the global `text`, or one problem naming the heading and a non-zero return. Fail closed:
# a renamed or deleted phase section is reported as missing rather than probed as an empty
# string, which would let "the section is gone" read as "the section says nothing wrong".
text=""
need_text() {
  text="$(doc_text "$skill_path" "$1" "${2-}")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no '$1' section to read — what that phase's leaf runs could not be established")
  return 1
}

# says <regex> <fact> — one thing the text in `$text` has to carry, written as the regex of
# any wording that would carry it; `fact` names it once if nothing matches.
says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

# says_fast_plus_affected <where> <why> — `$text` names the fast tier and the affected suites;
# <where> names the text read, <why> finishes "which …" in each problem.
says_fast_plus_affected() {
  says 'fast (tier|command)' "$1 never names the fast tier, which $2"
  says 'affected suites|suites affected-suites\.sh' "$1 never names the affected suites, which $2"
}

# paragraphs <file> — the file's blank-line-separated paragraphs, one per line, normalised
# through `plain`. CLAUDE.md is prose that wraps mid-sentence, so a paragraph is the unit a
# claim about it can be asked of: a match on the whole file would let "full suite" in one
# section answer for a leaf named in another.
paragraphs() {
  awk 'BEGIN { RS = "" } { gsub(/\n/, " "); print }' "$1" | plain
}

# 1. One criterion — the two documents agree with the prompts about which leaves run the
#    full suite — and so one case. The four SKILL.md probes and the two CLAUDE.md ones are
#    halves of one fact recorded in two places: a reader who finds the answer in one and the
#    stale rule in the other is worse off than one who finds it once, and the fix to any of
#    them is one edit to one document.
name="$skill_md's phase sections and $claude_md say which leaves run the full suite"
problems=()

# Red runs one suite: the only question the phase asks is whether one new case fails
# against unmodified code, which the suite holding that case answers.
if need_text '#### Red'; then
  says 'suite (that |which )?(holds|holding|contains|containing|carries)|case.s suite|suite the (new )?(case|test)' \
    "$skill_md's Red section never says the red leaf runs the suite holding its new case, so the conductor's account of that leaf is the full-suite one the prompt no longer gives"
fi

# Green is one of the two places the full-suite guarantee lives, so its section is where
# SKILL.md has to keep saying it.
if need_text '#### Green'; then
  says 'full suite' \
    "$skill_md's Green section never names the full suite, so the one developer leaf that does run it reads like the ones that do not"
fi

# Refactor is the biggest item on the cost axis — the budget lets one step run the suite
# six times — and the section states both halves: what the transform leaf runs, and where
# the full suite runs instead.
if need_text '#### Refactor loop'; then
  says 'suites (covering|that cover|which cover|of the touched)' \
    "$skill_md's Refactor loop section never says the transform leaf runs the suites covering the touched files — it still describes the full-suite run the prompt dropped"
fi
if need_text '#### Refactor loop' '^2\. '; then
  says 'full suite' \
    "$skill_md's Refactor loop never says the full suite runs at verify-refactor, so the phase's account drops the run that catches a break in an untouched suite"
fi

# And the document the next agent reads before touching any of this. The stale sentence is
# load-bearing prose — it is the reason docs suites live outside `make test`'s glob — so it
# has to be corrected, not deleted.
stale="$(grep -nE 'every [a-z]*[[:space:]]*leaf runs' "$claude_path")"
[[ -z "$stale" ]] ||
  problems+=("$claude_md still says every leaf runs the suite after every edit, which the red and refactor leaves no longer do: $stale")
# The paragraphs of CLAUDE.md that mention the full suite at all, read once and named:
# whether there are any, and whether they name the leaves, are two questions about that same
# text, and asking the second of a second pipeline lets the two drift apart.
full_suite_paragraphs="$(paragraphs "$claude_path" | grep -E 'full suite')"
[[ -n "$full_suite_paragraphs" ]] ||
  problems+=("$claude_md never names the full suite at all, so which leaves run it is recorded nowhere a reader of this repository would look")
grep -qE 'develop-green|verify-green|verifier' <<<"$full_suite_paragraphs" ||
  problems+=("$claude_md mentions the full suite without naming the leaves that run it (develop-green and the blind verifiers), so the rule reads as a description of every leaf again")

report "$name"

# 2. SKILL.md's verify-refactor entry — the Refactor loop's sub-step 5, up to sub-step 6 —
#    states the verdict in verify-refactor.md's own terms: the fast tier plus the affected
#    suites still green, and no full-suite run inside the refactor phase.
name="$skill_md's verify-refactor entry says the verdict is on the fast tier plus the affected suites, not the full suite"
problems=()
if need_text '#### Refactor loop' '^5\. '; then
  text="${text%%6. narrate*}"
  says_fast_plus_affected "$skill_md's verify-refactor entry" \
    'verify-refactor.md tells the verifier to run'
  [[ "$text" =~ full\ suite ]] &&
    problems+=("$skill_md's verify-refactor entry still says the full suite runs in the refactor phase, which verify-refactor.md never asks of the verifier")
fi
report "$name"

# 3. The sentence in the Refactor loop saying what catches a break in a suite outside the
#    affected set — from "break in a suite" to its full stop — names the Draft PR step's
#    full-suite run and its repair step, and no longer hands that break to verify-refactor.
#    A digit's full stop ("4. Draft PR") is masked first so it does not end the sentence.
name="$skill_md's sentence on a break outside the affected set points at the Draft PR step's full run and its repair step, not at verify-refactor"
problems=()
if need_text '#### Refactor loop'; then
  if [[ "$text" == *"break in a suite"* ]]; then
    text="${text#*break in a suite}"
    text="${text//[0-9]./#}"
    text="${text%%. *}"
    says 'draft pr' \
      "$skill_md's sentence on a break outside the affected set never names the Draft PR step, where the one full-suite run is"
    says 'full[- ]suite run|full run|full suite' \
      "$skill_md's sentence on a break outside the affected set never names the full-suite run that catches it"
    says 'repair step' \
      "$skill_md's sentence on a break outside the affected set never names the repair step a red full run appends"
    [[ "$text" =~ surfaces\ here|verify-refactor|verifier|reject ]] &&
      problems+=("$skill_md's sentence on a break outside the affected set still hands that break to verify-refactor")
  else
    problems+=("$skill_md's Refactor loop never says what catches a break in a suite outside the affected set")
  fi
fi
report "$name"

# 4. SKILL.md's develop-green entry — the Green section's sub-step 1, up to sub-step 2 —
#    says what develop-green.md tells the leaf to keep green before it reports: the fast
#    tier plus the affected suites, not the full suite.
name="$skill_md's Green entry says develop-green keeps the fast tier plus the affected suites green, not the full suite"
problems=()
if need_text '#### Green' '^1\. '; then
  text="${text%%2. verify*}"
  says_fast_plus_affected "$skill_md's develop-green entry" \
    'develop-green.md tells the leaf to run before it reports'
  [[ "$text" =~ full\ suite ]] &&
    problems+=("$skill_md's develop-green entry still says develop-green keeps the full suite green, which develop-green.md never asks of the leaf")
fi
report "$name"

# 5. CLAUDE.md's "Testing idiom" paragraph on where the docs suites live — the one opening
#    "a suite whose subject is the docs pipeline" — states what runs per step (red and
#    refactor leaves: the affected suites; develop-green, verify-green and verify-refactor:
#    the fast tier plus the affected suites) and per PR (the full suite once before the PR
#    is readied, plus once per repair step), and no longer says three leaves per step run it.
name="$claude_md's Testing idiom paragraph states what runs per step and per PR"
problems=()
text="$(paragraphs "$claude_path" | grep -E '^a suite whose subject is the docs pipeline')"
if [[ -n "$text" ]]; then
  says_fast_plus_affected "$claude_md's Testing idiom paragraph" \
    'develop-green, verify-green and verify-refactor run per step'
  says 'develop-green' "$claude_md's Testing idiom paragraph never names develop-green"
  says 'verify-green' "$claude_md's Testing idiom paragraph never names verify-green"
  says 'verify-refactor' "$claude_md's Testing idiom paragraph never names verify-refactor"
  says '(per|once a|each|one) pr|pr is readied|readying the pr|readies the pr' \
    "$claude_md's Testing idiom paragraph never says the full suite runs once per PR, before the PR is readied"
  says 'repair step' \
    "$claude_md's Testing idiom paragraph never says a repair step runs the full suite again"
  [[ "$text" =~ three\ leaves\ per\ step ]] &&
    problems+=("$claude_md's Testing idiom paragraph still says three leaves per step run the full suite")
else
  problems+=("$claude_md has no paragraph opening 'a suite whose subject is the docs pipeline' to read")
fi
report "$name"

# 6. A step's cycle — from the Red heading to "4. Draft PR" — names no full-suite run: every
#    "full suite" in it is negated, and a "full-suite run" points at the Draft PR step, so a
#    run carries one tier-all run per PR plus one per repair step.
name="$skill_md names no full-suite run inside a step's cycle"
problems=()
text="$(awk 'index($0, "#### Red") == 1 { s = 1 } index($0, "### 4. Draft PR") == 1 { exit } s' "$skill_path" | plain | tr -s '\n ' ' ')"
if [[ -n "${text// /}" ]]; then
  negated='(^| )(not|neither|nor|never|no)( [a-z-]+){0,5} full suite'
  to_draft_pr='full[- ]suite run (in|at) (4\. )?draft pr'
  while [[ "$text" =~ $negated ]]; do text="${text/"${BASH_REMATCH[0]}"/}"; done
  while [[ "$text" =~ $to_draft_pr ]]; do text="${text/"${BASH_REMATCH[0]}"/}"; done
  [[ "$text" =~ [^.]{0,60}(full\ suite|full-suite\ run)[^.]{0,40} ]] &&
    problems+=("$skill_md names a full-suite run inside a step's cycle: ${BASH_REMATCH[0]}")
else
  problems+=("$skill_md has no text from '#### Red' to '### 4. Draft PR' to read")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

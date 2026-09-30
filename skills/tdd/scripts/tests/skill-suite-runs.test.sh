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
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"


source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

doc_text() {
  awk -v h="$2" -v from="$3" '
    !in_s && index($0, h) == 1 { in_s = 1; want = (from == "" ? 1 : 0); next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$1" | plain | tr '\n' ' '
}

text=""
need_text() {
  text="$(doc_text "$skill_path" "$1" "${2-}")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no '$1' section to read — what that phase's leaf runs could not be established")
  return 1
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

says_fast_plus_affected() {
  says 'fast (tier|command)' "$1 never names the fast tier, which $2"
  says 'affected suites|suites affected-suites\.sh' "$1 never names the affected suites, which $2"
}

paragraphs() {
  awk 'BEGIN { RS = "" } { gsub(/\n/, " "); print }' "$1" | plain
}

name="$skill_md's phase sections and $claude_md say which leaves run the full suite"
problems=()

if need_text '#### Red'; then
  says 'suite (that |which )?(holds|holding|contains|containing|carries)|case.s suite|suite the (new )?(case|test)' \
    "$skill_md's Red section never says the red leaf runs the suite holding its new case, so the conductor's account of that leaf is the full-suite one the prompt no longer gives"
fi

if need_text '#### Green'; then
  says 'full suite' \
    "$skill_md's Green section never names the full suite, so the one developer leaf that does run it reads like the ones that do not"
fi

if need_text '#### Refactor loop'; then
  says 'suites (covering|that cover|which cover|of the touched)' \
    "$skill_md's Refactor loop section never says the transform leaf runs the suites covering the touched files — it still describes the full-suite run the prompt dropped"
fi
if need_text '#### Refactor loop' '^2\. '; then
  says 'full suite' \
    "$skill_md's Refactor loop never says the full suite runs at verify-refactor, so the phase's account drops the run that catches a break in an untouched suite"
fi

stale="$(grep -nE 'every [a-z]*[[:space:]]*leaf runs' "$claude_path")"
[[ -z "$stale" ]] ||
  problems+=("$claude_md still says every leaf runs the suite after every edit, which the red and refactor leaves no longer do: $stale")
full_suite_paragraphs="$(paragraphs "$claude_path" | grep -E 'full suite')"
[[ -n "$full_suite_paragraphs" ]] ||
  problems+=("$claude_md never names the full suite at all, so which leaves run it is recorded nowhere a reader of this repository would look")
grep -qE 'develop-green|verify-green|verifier' <<<"$full_suite_paragraphs" ||
  problems+=("$claude_md mentions the full suite without naming the leaves that run it (develop-green and the blind verifiers), so the rule reads as a description of every leaf again")

report "$name"

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

finish

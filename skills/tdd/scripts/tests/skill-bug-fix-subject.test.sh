#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to write on the subject line
# of a bug run's commits and PR. Like skill-green-split.test.sh and skill-commit.test.sh
# this suite belongs to no single script: its subject is the procedure document, read as
# text, the way the session that follows it reads it. Picked up by `make test`'s glob by
# existing. Zero-dependency plain-shell asserts, same idiom as skill-green-split.test.sh.
#
# Why this exists (issue #112): a bug's Red is a reproduction, and the fix that turns it
# green is not a new capability. The walkthrough's capability index is computed from the
# `feat:`/`fix:` commits in each tag's range, so a bug step whose green commit lands as
# `feat:` tells the index a capability arrived where a regression was repaired, and a PR
# titled `feat:` says the same thing to the human deciding the merge. Both subject lines
# exist only because SKILL.md dictates them — the scripts never compose a commit message —
# so a document that goes on saying `feat:` unconditionally is the whole of the regression.
#
# Contract under test (this step only):
#   SKILL.md's Green section says a bug step's green commit takes a `fix:` subject, and its
#   Draft PR step says a bug run's PR title starts with the `fix:` prefix.
#
# Run: scripts/tests/skill-bug-fix-subject.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice, the way skill-green-split.test.sh names its two: the path as every
# failure message spells it, and the same path resolved for the probes to read, so a message
# can never name a file the probes did not open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which subject line is missing rather than just that one is.
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
# joined onto one, because `fix:` and **fix:** are the same token and a sentence that wraps
# across two lines is still one sentence. The probes' regexes are then written one way and
# match however the author chose to mark the words up.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# section <heading-prefix> — the lines after the first heading STARTING WITH that literal,
# up to the next heading of any level, normalised through `plain`. A literal prefix rather
# than a whole heading because both of these carry trailing prose the writer may reword.
section() {
  awk -v h="$1" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain
}

# The two headings, spelled once each: the probes find the sections by them and the
# fail-closed messages name them, so a suite re-pointed at a renamed heading cannot go on
# telling a reader it searched for the old one.
green_heading='#### Green'
pr_heading='### 4. Draft PR'

# window <text> <extended-regex> — the text within 250 characters either side of the first
# match, or the empty string when there is none: what a reader meets while working out
# which subject line this run owes. 250 rather than a rounder, larger number because BSD
# grep — the one on the development machine this repository holds itself portable to —
# refuses an interval whose bound is over 255.
window() {
  head -1 < <(grep -oE ".{0,250}$2.{0,250}" <<<"$1")
}

# probe_fix_line <heading> <unestablished> <absent> <unqualified> — the one shape both
# subject lines are read by, appending at most one problem to `problems`: the section is
# missing (fail closed, naming the heading and what could not be established), or it never
# names `fix:` at all, or it names it without `bug` anywhere near, which leaves a second
# subject line in the document and nothing saying which runs take it. The three messages come
# in from the call site because only they differ between the two lines — the branch does not.
probe_fix_line() {
  local heading="$1" unestablished="$2" absent="$3" unqualified="$4" text
  text="$(section "$heading")"
  if [[ -z "${text// /}" ]]; then
    problems+=("$skill_md has no '$heading' section to read — $unestablished")
  elif ! grep -qE 'fix:' <<<"$text"; then
    problems+=("$absent")
  else
    grep -qE 'bug' <<<"$(window "$text" 'fix:')" || problems+=("$unqualified")
  fi
}

# The criterion, as one case: both subject lines are the same decision — a bug's repair is
# not a capability — and a document that said it in one place and not the other would leave
# the run's own commits disagreeing with the PR that carries them.
name="$skill_md gives a bug step's green commit a fix: subject and a bug run's PR title a fix: prefix"
problems=()

probe_fix_line "$green_heading" \
  "what subject a bug step's green commit takes could not be established" \
  "$skill_md's '$green_heading' section never names a fix: subject, so a bug step's green commit lands as feat: and the capability index reads a repaired regression as a new capability" \
  "$skill_md's '$green_heading' section names a fix: subject without saying it is a bug step's, so the conductor is given a second subject line and nothing that says which steps take it"

probe_fix_line "$pr_heading" \
  "what prefix a bug run's PR title takes could not be established" \
  "$skill_md's '$pr_heading' section never names the fix: prefix, so a bug run opens a PR whose title announces a capability the run did not add" \
  "$skill_md's '$pr_heading' section names the fix: prefix without saying it is a bug run's, so the conductor cannot tell which runs title their PR that way"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

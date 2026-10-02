#!/usr/bin/env bash
# Unit tests for scripts/refactor-owed.sh — the file that carries a run's structural
# leftovers from each step's refactor loop into the draft PR.
#
# Contract under test:
#   refactor-owed.sh appends a step's structural candidates to
#   `.tdd/issue-<n>-refactor-owed.md` and renders that file as a PR-body section.
#
# Run: scripts/tests/refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OWED="$HERE/../refactor-owed.sh"

source "$HERE/lib/harness.sh"

line_of() {
  head -1 < <(grep -nF "$2" "$1") | cut -d: -f1
}

answers_none_on() {
  local verb="$1" owed_file="$2" what="$3" why="$4" out code printed
  out="$(mktemp)"
  "$OWED" "$verb" "$owed_file" >"$out" 2>/dev/null && code=0 || code=$?

  [[ "$code" == 3 ]] ||
    problems+=("want exit 3 from $verb on $what, got $code")

  printed="$(cat "$out")"
  [[ -z "$printed" ]] ||
    problems+=("$verb printed '$printed' on stdout for $what$why")

  rm -f "$out"
}

answers_none() {
  local verb="$1" why="$2" missing_file empty_file
  missing_file="$(mktemp)"
  rm -f "$missing_file"
  empty_file="$(mktemp)"

  answers_none_on "$verb" "$missing_file" "an absent file" "$why"
  answers_none_on "$verb" "$empty_file" "a file holding no candidate" "$why"

  rm -f "$empty_file"
}

lists_as() {
  local owed_file="$1" why="$2" listed want code
  want="$(mktemp)"
  cat >"$want"

  listed="$(mktemp)"
  "$OWED" list "$owed_file" >"$listed" 2>/dev/null && code=0 || code=$?

  [[ "$code" == 0 ]] ||
    problems+=("want exit 0 from list, got $code")

  diff "$want" "$listed" >/dev/null ||
    problems+=("list printed:" "$(cat "$listed")" "$why" "$(cat "$want")")

  rm -f "$listed" "$want"
}

under_step() {
  local file="$1" step="$2" transform="$3" step_at candidate_at
  step_at="$(line_of "$file" "$step")"
  candidate_at="$(line_of "$file" "$transform")"
  if [[ -z "$candidate_at" ]]; then
    problems+=("$file does not carry the candidate '$transform'")
  elif [[ -z "$step_at" ]]; then
    problems+=("$file carries '$transform' but never names the step '$step' that owes it")
  elif [[ "$step_at" -gt "$candidate_at" ]]; then
    problems+=("$file names the step '$step' on line $step_at, below its candidate '$transform' on line $candidate_at — the candidate is not under its step")
  fi
}

name="append writes only the structural candidates to the file, under the named step"
problems=()

owed_file="$(mktemp)"
step='refactor-owed.sh append writes only the structural CANDIDATES lines'
"$OWED" append "$owed_file" "$step" <<'REPORT' && code=0 || code=$?
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from append, got $code")

while IFS= read -r transform; do
  hits="$(grep -cF "$transform" "$owed_file")"
  [[ "$hits" == 1 ]] ||
    problems+=("want the structural candidate '$transform' on exactly 1 line of $owed_file, found on $hits")
done <<'STRUCTURAL'
fold verify.sh's two mktemp calls into one helper
rename $tmp to $prompt_file, which is what it holds
STRUCTURAL

cosmetic='reflow the header comment to ninety columns'
grep -qF "$cosmetic" "$owed_file" &&
  problems+=("the cosmetic candidate '$cosmetic' is in $owed_file; only structural leftovers are work a follow-up owes")

under_step "$owed_file" "$step" 'fold verify.sh'"'"'s two mktemp calls into one helper'

rm -f "$owed_file"
report "$name"

name="two append calls for different steps leave both steps' candidates in the file"
problems=()

owed_file="$(mktemp)"
first_step='refactor-owed.sh append writes only the structural CANDIDATES lines'
second_step='two append calls for different steps keep both steps'
"$OWED" append "$owed_file" "$first_step" <<'REPORT' && code=0 || code=$?
RESULT: applied "split the verdict parser out of run-leaf.sh", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
REPORT
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the first append, got $code")
"$OWED" append "$owed_file" "$second_step" <<'REPORT' && code=0 || code=$?
RESULT: applied "name the ledger path once", suite green
FLAGS: none
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the second append, got $code")

for wanted in \
  "$first_step" \
  "$second_step" \
  "fold verify.sh's two mktemp calls into one helper" \
  "hoist the ledger path into one variable"
do
  grep -qF "$wanted" "$owed_file" ||
    problems+=("'$wanted' is not in $owed_file; the second append did not add to what the first wrote")
done

rm -f "$owed_file"
report "$name"

name="render prints a ## Refactor owed section listing every recorded candidate under its step"
problems=()

owed_file="$(mktemp)"
first_step='refactor-owed.sh append writes only the structural CANDIDATES lines'
second_step='refactor-owed.sh render prints a Refactor owed section'
"$OWED" append "$owed_file" "$first_step" <<'REPORT'
RESULT: applied "split the verdict parser out of run-leaf.sh", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
REPORT
"$OWED" append "$owed_file" "$second_step" <<'REPORT'
RESULT: applied "name the ledger path once", suite green
FLAGS: none
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

rendered="$(mktemp)"
"$OWED" render "$owed_file" >"$rendered" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from render, got $code")

grep -qF '## Refactor owed' "$rendered" ||
  problems+=("render printed no '## Refactor owed' heading, so its output is not a section a PR body can carry")

under_step "$rendered" "$first_step" "fold verify.sh's two mktemp calls into one helper"
under_step "$rendered" "$second_step" 'hoist the ledger path into one variable'
under_step "$rendered" "$second_step" 'rename $tmp to $prompt_file, which is what it holds'

rm -f "$owed_file" "$rendered"
report "$name"


name="render exits 3 and prints nothing when the file is absent or holds no candidate"
problems=()

answers_none render "; a PR body must not carry a heading promising leftovers nobody left"
report "$name"


name="list prints every recorded candidate one per line without step headings, and exits 3 on none"
problems=()

owed_file="$(mktemp)"
"$OWED" append "$owed_file" 'first step' <<'REPORT'
RESULT: applied "split the verdict parser out of run-leaf.sh", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
REPORT
"$OWED" append "$owed_file" 'second step' <<'REPORT'
RESULT: applied "name the ledger path once", suite green
FLAGS: none
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

lists_as "$owed_file" "want exactly the three candidates, one per line, no step heading:" <<'WANT'
fold verify.sh's two mktemp calls into one helper
hoist the ledger path into one variable
rename $tmp to $prompt_file, which is what it holds
WANT

rm -f "$owed_file"

answers_none list "; want nothing"
report "$name"


name="list prints each candidate once, those recorded under more steps first, ties in recorded order"
problems=()

owed_file="$(mktemp)"
"$OWED" append "$owed_file" 'first step' <<'REPORT'
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
"$OWED" append "$owed_file" 'second step' <<'REPORT'
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT
"$OWED" append "$owed_file" 'third step' <<'REPORT'
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | split the verdict parser out of run-leaf.sh
REPORT

lists_as "$owed_file" "want each candidate once, three steps before two before one, the two recorded once in recorded order:" <<'WANT'
hoist the ledger path into one variable
rename $tmp to $prompt_file, which is what it holds
fold verify.sh's two mktemp calls into one helper
split the verdict parser out of run-leaf.sh
WANT

rm -f "$owed_file"
report "$name"


name="append keeps a test-only candidate in the file, under the named step"
problems=()

owed_file="$(mktemp)"
step='refactor-owed.sh append keeps a test-only candidate under its step'
"$OWED" append "$owed_file" "$step" <<'REPORT' && code=0 || code=$?
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: test-only | fold the three answers_none fixtures into one helper
REPORT

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from append, got $code")

under_step "$owed_file" "$step" 'fold the three answers_none fixtures into one helper'

rm -f "$owed_file"
report "$name"


name="list never prints a test-only candidate, and exits 3 on a file holding only those"
problems=()

owed_file="$(mktemp)"
"$OWED" append "$owed_file" 'a step whose candidates are all test-only' <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: test-only | fold the three answers_none fixtures into one helper
REPORT

answers_none_on list "$owed_file" "a file holding only test-only candidates" "; want nothing"

rm -f "$owed_file"
report "$name"


name="list prints a file's structural candidates exactly as it does with its test-only ones absent"
problems=()

alone_file="$(mktemp)"
both_file="$(mktemp)"
"$OWED" append "$alone_file" 'first step' <<'REPORT'
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
"$OWED" append "$alone_file" 'second step' <<'REPORT'
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
"$OWED" append "$both_file" 'first step' <<'REPORT'
CANDIDATES: test-only | fold the three answers_none fixtures into one helper
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: test-only | rename $owed_file to $ledger in the list cases
CANDIDATES: structural | hoist the ledger path into one variable
REPORT
"$OWED" append "$both_file" 'second step' <<'REPORT'
CANDIDATES: test-only | fold the three answers_none fixtures into one helper
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: test-only | rename $owed_file to $ledger in the list cases
REPORT

lists_as "$both_file" "want what list prints for the structural candidates alone:" < <("$OWED" list "$alone_file")

rm -f "$alone_file" "$both_file"
report "$name"


name="render prints the test-only candidates under a heading of their own inside ## Refactor owed, saying the structural pass does not work them"
problems=()

owed_file="$(mktemp)"
"$OWED" append "$owed_file" 'first step' <<'REPORT'
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: test-only | fold the three answers_none fixtures into one helper
REPORT
"$OWED" append "$owed_file" 'second step' <<'REPORT'
CANDIDATES: test-only | rename $owed_file to $ledger in the list cases
CANDIDATES: structural | hoist the ledger path into one variable
REPORT

rendered="$(mktemp)"
"$OWED" render "$owed_file" >"$rendered" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from render, got $code")

section_at="$(line_of "$rendered" '## Refactor owed')"
heading="$(head -1 < <(grep -nE '^###+ .*[Tt]est-only' "$rendered"))"
if [[ -z "$section_at" ]]; then
  problems+=("render printed no '## Refactor owed' heading")
elif [[ -z "$heading" ]]; then
  problems+=("render printed no heading of their own for the test-only candidates:" "$(cat "$rendered")")
else
  heading_at="${heading%%:*}"
  heading_text="${heading#*:}"
  level="${heading_text%%[^#]*}"
  own_section="$(awk -v from="$heading_at" -v level="${#level}" '
    NR > from && match($0, /^#+ /) && RLENGTH - 1 <= level { exit }
    NR >= from' "$rendered")"

  [[ "$heading_at" -gt "$section_at" ]] ||
    problems+=("the test-only heading on line $heading_at is not inside '## Refactor owed' on line $section_at")

  for transform in \
    'fold the three answers_none fixtures into one helper' \
    'rename $owed_file to $ledger in the list cases'
  do
    [[ "$own_section" == *"$transform"* ]] ||
      problems+=("the test-only candidate '$transform' is not under the heading '$heading_text':" "$own_section")
    times="$(grep -cF -- "$transform" "$rendered" || true)"
    [[ "$times" == 1 ]] ||
      problems+=("the test-only candidate '$transform' is printed $times times, want once, under '$heading_text' only:" "$(cat "$rendered")")
  done

  for transform in \
    "fold verify.sh's two mktemp calls into one helper" \
    'hoist the ledger path into one variable'
  do
    [[ "$own_section" != *"$transform"* ]] ||
      problems+=("the structural candidate '$transform' is under the test-only heading '$heading_text'")
  done

  [[ "$own_section" == *"structural pass"* ]] ||
    problems+=("nothing under the heading '$heading_text' says the structural pass does not work them:" "$own_section")
fi

rm -f "$owed_file" "$rendered"
report "$name"


name="render prints a file holding only structural candidates exactly as before, with no test-only heading"
problems=()

owed_file="$(mktemp)"
"$OWED" append "$owed_file" 'first step' <<'REPORT'
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | rename $tmp to $prompt_file
REPORT

want="$(mktemp)"
{ printf '## Refactor owed\n\n'; cat "$owed_file"; } >"$want"

rendered="$(mktemp)"
"$OWED" render "$owed_file" >"$rendered" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from render, got $code")

diff "$want" "$rendered" >/dev/null ||
  problems+=("render printed:" "$(cat "$rendered")" "want:" "$(cat "$want")")

rm -f "$owed_file" "$want" "$rendered"
report "$name"


finish

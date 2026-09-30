#!/usr/bin/env bash
# Unit tests for scripts/refactor-owed.sh — the file that carries a run's structural
# leftovers from each step's refactor loop into the draft PR. Zero-dependency plain-shell
# asserts, same idiom as refactor-triage.test.sh, the suite for the script whose answer
# ends that loop.
#
# Why this exists (issue #359, part of #354): when a step's refactor stops with structural
# candidates still listed, nothing records them. `.tdd/develop-refactor.out` is overwritten
# by the next step, so by the draft PR every step's leftovers but the last are gone. This
# script appends them to `.tdd/issue-<n>-refactor-owed.md`, which the ledger's .gitignore
# rule already tracks, and renders them as a PR-body section.
#
# Run: scripts/tests/refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OWED="$HERE/../refactor-owed.sh"

source "$HERE/lib/harness.sh"

line_of() {
  head -1 < <(grep -nF "$2" "$1") | cut -d: -f1
}

answers_none() {
  local verb="$1" why="$2" missing_file empty_file owed_file what out code printed
  missing_file="$(mktemp)"
  rm -f "$missing_file"
  empty_file="$(mktemp)"

  for owed_file in "$missing_file" "$empty_file"; do
    [[ "$owed_file" == "$missing_file" ]] && what="an absent file" || what="a file holding no candidate"

    out="$(mktemp)"
    "$OWED" "$verb" "$owed_file" >"$out" 2>/dev/null && code=0 || code=$?

    [[ "$code" == 3 ]] ||
      problems+=("want exit 3 from $verb on $what, got $code")

    printed="$(cat "$out")"
    [[ -z "$printed" ]] ||
      problems+=("$verb printed '$printed' on stdout for $what$why")

    rm -f "$out"
  done

  rm -f "$empty_file"
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

listed="$(mktemp)"
"$OWED" list "$owed_file" >"$listed" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from list, got $code")

want="$(mktemp)"
cat >"$want" <<'WANT'
fold verify.sh's two mktemp calls into one helper
hoist the ledger path into one variable
rename $tmp to $prompt_file, which is what it holds
WANT
diff "$want" "$listed" >/dev/null ||
  problems+=("list printed:" "$(cat "$listed")" "want exactly the three candidates, one per line, no step heading:" "$(cat "$want")")

rm -f "$owed_file" "$listed" "$want"

answers_none list "; want nothing"
report "$name"


finish

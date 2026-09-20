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
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did. Same helper
# refactor-triage.test.sh uses.
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

# line_of <file> <needle> — the 1-based number of the first line of <file> holding <needle>,
# or the empty string when none does. Two cases below ask the same ordering question of two
# different files — whether `append` wrote a candidate under its step, and whether `render`
# printed it under its step — and a position is what turns two "is it there?" probes into it.
# -F throughout: a transform is matched as the literal a leaf wrote, not as a pattern, since
# `$` and `'` are ordinary characters in one. Suite-local helper, the same idiom
# refactor-triage.test.sh's own `line_of` follows.
line_of() {
  grep -nF "$2" "$1" | head -1 | cut -d: -f1
}

# 1. what `append` keeps. A develop-refactor report piped in carries both classes of
#    candidate — structural and cosmetic, as prompts/develop-refactor.md's *The two classes
#    of candidate* defines them — and only the structural ones are work a follow-up owes.
#    A cosmetic leftover written into the file would put a reflowed comment in front of the
#    human deciding the merge, which is the mixed backlog #149 already refused once.
#
#    The step name is the other half: the file accumulates across a whole run, so a
#    candidate that does not say which step left it behind cannot be acted on. "Under that
#    step" is pinned as order — the step's name appears before its candidates — not as a
#    heading syntax, which is the script's business.
#
#    The fixture is a whole report rather than bare candidate lines because that is what the
#    conductor pipes in: the leaf's last lines, verbatim (develop-refactor.md, *Report*).
#    It is written to a file rather than through `$(cat <<'REPORT' … )` for the reason
#    refactor-triage.test.sh records: a command substitution is scanned for its closing
#    paren without regard for the heredoc inside it, so the apostrophe in `verify.sh's`
#    below would read as an unterminated quote.
name="append writes only the structural candidates to the file, under the named step"
problems=()

leaf_report="$(mktemp)"
cat > "$leaf_report" <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

owed_file="$(mktemp)"
step='refactor-owed.sh append writes only the structural CANDIDATES lines'
"$OWED" append "$owed_file" "$step" <"$leaf_report" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from append, got $code")

# -F so a transform is matched as the literal a leaf wrote, not as a pattern: `$` and `'`
# are ordinary characters in a candidate.
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

# Order rather than syntax: the step is named, and it is named before the candidates it
# left behind, which is the whole of what "under that step" means to a reader.
step_at="$(line_of "$owed_file" "$step")"
first_candidate_at="$(line_of "$owed_file" 'fold verify.sh'"'"'s two mktemp calls into one helper')"
if [[ -z "$step_at" ]]; then
  problems+=("$owed_file never names the step '$step', so nothing says which step owes these candidates")
elif [[ -n "$first_candidate_at" && "$step_at" -gt "$first_candidate_at" ]]; then
  problems+=("$owed_file names the step on line $step_at, after its first candidate on line $first_candidate_at — the candidates are not under the step")
fi

rm -f "$leaf_report" "$owed_file"
report "$name"

# 2. what a second `append` does to what the first wrote. The file accumulates across a
#    whole run — one call per step, from SKILL.md's Refactor section — and `.tdd/develop-
#    refactor.out` losing every step's leftovers but the last is the whole bug #359 names.
#    So a second call must add to the file, never replace it: after two calls for different
#    steps, both steps and both steps' candidates are still there.
#
#    Two probes, because one alone would pass on a broken script: candidates alone would
#    pass a file that lost the first step's *name*, and names alone would pass one that kept
#    both headings and dropped the earlier transform.
name="two append calls for different steps leave both steps' candidates in the file"
problems=()

first_report="$(mktemp)"
cat > "$first_report" <<'REPORT'
RESULT: applied "split the verdict parser out of run-leaf.sh", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
REPORT

second_report="$(mktemp)"
cat > "$second_report" <<'REPORT'
RESULT: applied "name the ledger path once", suite green
FLAGS: none
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | hoist the ledger path into one variable
REPORT

owed_file="$(mktemp)"
first_step='refactor-owed.sh append writes only the structural CANDIDATES lines'
second_step='two append calls for different steps keep both steps'
"$OWED" append "$owed_file" "$first_step" <"$first_report" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the first append, got $code")
"$OWED" append "$owed_file" "$second_step" <"$second_report" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the second append, got $code")

# -F throughout: a transform is matched as the literal a leaf wrote, and `$` and `'` are
# ordinary characters in one.
for wanted in \
  "$first_step" \
  "$second_step" \
  "fold verify.sh's two mktemp calls into one helper" \
  "hoist the ledger path into one variable"
do
  grep -qF "$wanted" "$owed_file" ||
    problems+=("'$wanted' is not in $owed_file; the second append did not add to what the first wrote")
done

rm -f "$first_report" "$second_report" "$owed_file"
report "$name"

# 3. what `render` prints. The owed file accumulates one section per step across a whole
#    run, and the draft PR is where it is finally read: SKILL.md's Draft PR section puts
#    this output in the body, so the human deciding the merge sees the leftovers #359 says
#    were being lost. The section's own heading — `## Refactor owed` — is the one piece of
#    syntax the criterion names, because the PR body is markdown and the section has to sit
#    in it as a section.
#
#    The file is built by `append`, not written here by hand: `render` reads what `append`
#    writes, so a fixture spelled out in the test would pin the file format — the script's
#    business, and the only thing case 1 deliberately did not assert.
#
#    Two steps, two candidates each side of the split, so "under its step" is a real probe:
#    every candidate is printed *after* the step that left it behind, which is what the
#    grouping means to a reader. Cosmetic lines are absent from the file already, so this
#    case says nothing about them.
name="render prints a ## Refactor owed section listing every recorded candidate under its step"
problems=()

first_report="$(mktemp)"
cat > "$first_report" <<'REPORT'
RESULT: applied "split the verdict parser out of run-leaf.sh", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
REPORT

second_report="$(mktemp)"
cat > "$second_report" <<'REPORT'
RESULT: applied "name the ledger path once", suite green
FLAGS: none
CANDIDATES: structural | hoist the ledger path into one variable
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

owed_file="$(mktemp)"
first_step='refactor-owed.sh append writes only the structural CANDIDATES lines'
second_step='refactor-owed.sh render prints a Refactor owed section'
"$OWED" append "$owed_file" "$first_step" <"$first_report"
"$OWED" append "$owed_file" "$second_step" <"$second_report"

rendered="$(mktemp)"
"$OWED" render "$owed_file" >"$rendered" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from render, got $code")

grep -qF '## Refactor owed' "$rendered" ||
  problems+=("render printed no '## Refactor owed' heading, so its output is not a section a PR body can carry")

# Every recorded candidate is printed, and printed after the step that left it behind.
# Paired step-and-candidate probes rather than two separate lists: a render that printed
# both steps and both candidates in the wrong order would pass a list of each.
check_under() {
  local step="$1" transform="$2" step_at candidate_at
  step_at="$(line_of "$rendered" "$step")"
  candidate_at="$(line_of "$rendered" "$transform")"
  if [[ -z "$candidate_at" ]]; then
    problems+=("render did not print the recorded candidate '$transform'")
  elif [[ -z "$step_at" ]]; then
    problems+=("render printed '$transform' but never names the step '$step' that owes it")
  elif [[ "$step_at" -gt "$candidate_at" ]]; then
    problems+=("render printed '$transform' on line $candidate_at, above its step '$step' on line $step_at — it is not under its step")
  fi
}

check_under "$first_step" "fold verify.sh's two mktemp calls into one helper"
check_under "$second_step" 'hoist the ledger path into one variable'
check_under "$second_step" 'rename $tmp to $prompt_file, which is what it holds'

rm -f "$first_report" "$second_report" "$owed_file" "$rendered"
report "$name"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

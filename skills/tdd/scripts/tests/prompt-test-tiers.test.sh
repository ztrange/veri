#!/usr/bin/env bash
# Tests for which test command each phase's prompt tells its leaf to run (issue #341) — like
# skill-test-command.test.sh this suite belongs to no single script: its subject is the
# prompt templates under scripts/prompts/, read the way a leaf reads them, as the prompt
# build-develop-prompt.sh and build-verify-prompt.sh assemble from them.
# Zero-dependency plain-shell asserts, same idiom as skill-red-prediction.test.sh.
#
# Why this exists: every phase of a cycle ran either the full suite or "the suite that holds
# the new case", a suite the leaf picked by hand. #337 added affected-suites.sh, which
# computes the suites one change affects, so a red leaf and its verifier run what that
# script prints rather than one suite someone chose — a hand-picked suite misses the guard
# suite that reads the same file, and the full command is a cost the red phase never needed.
#
# Contract under test (this step only):
#   the assembled develop-red and verify-red prompts each name affected-suites.sh as what
#   the leaf runs, and develop-red no longer tells its leaf to run the one suite that holds
#   the new case.
#
# Run: scripts/tests/prompt-test-tiers.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEVELOP="$HERE/../build-develop-prompt.sh"
VERIFY="$HERE/../build-verify-prompt.sh"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

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

# plain — stdin with emphasis marks and backticks dropped and the case folded, so the
# probes match however a template marks the words up.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# runs_affected <phase label> <prompt> — the prompt has a line that tells the leaf to run
# what affected-suites.sh prints, not merely one that mentions the script.
runs_affected() {
  local label="$1" prompt="$2"
  if ! plain <<< "$prompt" | grep -E 'affected-suites\.sh' | grep -qE '\brun'; then
    problems+=("$label's prompt never tells its leaf to run the suites affected-suites.sh prints")
  fi
}

printf 'zorblat must return frob\n' > "$work/spec.md"

# 1. The red leaf and its verifier run the affected suites (criterion 2).
name="develop-red and verify-red name affected-suites.sh, not one hand-named suite, as what they run"
problems=()
red="$("$DEVELOP" red "$work/spec.md" 'QWIXTLE step' 'make test' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh red exited $?")
verify_red="$("$VERIFY" red "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh red exited $?")
runs_affected develop-red "$red"
runs_affected verify-red "$verify_red"
if plain <<< "$red" | grep -qE 'run the suite that holds the new case'; then
  problems+=("develop-red still tells its leaf to run the one suite that holds the new case")
fi
report "$name"

# 2. verify-refactor's checklist item 1 runs the affected suites (criterion 3). The item is
#    read on its own — from its `1.` line up to the `2.` one — so a mention elsewhere in the
#    prompt cannot satisfy it.
name="verify-refactor's checklist item 1 names affected-suites.sh, not the project's full test suite"
problems=()
verify_refactor="$("$VERIFY" refactor "$work/spec.md" 'tests/zorblat.test.sh' 'abc1234' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh refactor exited $?")
item1="$(plain <<< "$verify_refactor" | awk 'f && /^2\. /{exit} f; /^1\. still green/{f=1; print}')"
if [[ -z "$item1" ]]; then
  problems+=("verify-refactor's prompt has no checklist item 1 ('1. still green')")
fi
if grep -qF "the project's full test suite" <<< "$item1"; then
  problems+=("verify-refactor's checklist item 1 still says \"the project's full test suite\"")
fi
runs_affected "verify-refactor's checklist item 1" "$item1"
report "$name"

# 3. The refactor leaf runs, after each transform, the suites affected-suites.sh prints when
#    fed refactor-touched.sh's output. The instruction that runs after each transform is read
#    on its own — the numbered item that says "after each transform", joined onto one line so
#    a template may wrap it anywhere — so a mention elsewhere in the prompt cannot satisfy it.
name="develop-refactor runs affected-suites.sh fed refactor-touched.sh's output after each transform"
problems=()
refactor="$("$DEVELOP" refactor "$work/spec.md" 'QWIXTLE step' 'make test' 'src/zorblat.sh' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh refactor exited $?")
after_each="$(plain <<< "$refactor" |
  awk '/^[0-9]+\. /{if (item ~ /after each transform/) {print item; exit} item=""} /^[0-9]+\. /||item!=""{item=item " " $0} END{if (item ~ /after each transform/) print item}')"
if [[ -z "$after_each" ]]; then
  problems+=("develop-refactor's prompt has no numbered item saying what runs after each transform")
fi
runs_affected "develop-refactor's after-each-transform item" "$after_each"
if ! grep -qF 'refactor-touched.sh' <<< "$after_each"; then
  problems+=("develop-refactor's after-each-transform item never feeds affected-suites.sh refactor-touched.sh's output")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

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

# runs_fast_plus_affected <phase label> <prompt> — the prompt names detect-test-command.sh's
# `--tier fast`, tells the leaf to run what affected-suites.sh prints, and no longer tells it
# to run, or keep green, the full suite.
runs_fast_plus_affected() {
  local label="$1" prompt="$2"
  if ! plain <<< "$prompt" | grep -qF -- '--tier fast'; then
    problems+=("$label's prompt never names the fast command (detect-test-command.sh --tier fast)")
  fi
  runs_affected "$label" "$prompt"
  if plain <<< "$prompt" | grep -qE "run (the )?(project's )?full (test )?suite|full suite (is )?green"; then
    problems+=("$label's prompt still tells its leaf to run, or keep green, the full suite")
  fi
}

# timed_through <phase label> <prompt> <tier> [tier …] — the prompt names timed-test-run.sh
# at a path the leaf can run (a leaf works in the target repository, where the bare name
# resolves to nothing), and tells its leaf to run through that wrapper under each tier
# named — the wrapper's first argument, and what every later reader groups by.
timed_through() {
  local label="$1" prompt="$2"; shift 2
  local runnable="" cand tier
  while read -r cand; do
    [[ -x "$cand" ]] && runnable="$cand"
  done < <(grep -oE '[^ `]*timed-test-run\.sh' <<< "$prompt")
  if [[ -z "$runnable" ]]; then
    problems+=("$label's prompt never names timed-test-run.sh at a path the leaf can run")
  fi
  for tier in "$@"; do
    if ! plain <<< "$prompt" | grep -qE "timed-test-run\.sh $tier\b"; then
      problems+=("$label's prompt never tells its leaf to run through timed-test-run.sh under tier $tier")
    fi
  done
}

# numbered_item <ere> — from the prompt on stdin, the first numbered item (`N. ` up to the
# next `N. `) whose text matches <ere>, printed as the item's own lines. <ere> is matched
# against the item joined onto one line (each line preceded by a space), so a template may
# wrap the matched words anywhere; the lines stay unjoined so runs_affected still demands
# "run" and affected-suites.sh on one line. Reading the item on its own means a mention
# elsewhere cannot satisfy a probe.
numbered_item() {
  awk -v re="$1" '
    /^[0-9]+\. /{if (item ~ re) {printf "%s", lines; done=1; exit} item=""; lines=""}
    /^[0-9]+\. /||item!=""{item=item " " $0; lines=lines $0 "\n"}
    END{if (!done && item ~ re) printf "%s", lines}'
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

# 2. verify-refactor's checklist item 1 runs the affected suites (criterion 3), read on its
#    own through numbered_item.
name="verify-refactor's checklist item 1 names affected-suites.sh, not the project's full test suite"
problems=()
verify_refactor="$("$VERIFY" --fast-cmd 'make unit' refactor "$work/spec.md" 'tests/zorblat.test.sh' 'abc1234' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh refactor exited $?")
item1="$(plain <<< "$verify_refactor" | numbered_item '^ 1\. still green')"
if [[ -z "$item1" ]]; then
  problems+=("verify-refactor's prompt has no checklist item 1 ('1. still green')")
fi
if grep -qF "the project's full test suite" <<< "$item1"; then
  problems+=("verify-refactor's checklist item 1 still says \"the project's full test suite\"")
fi
runs_affected "verify-refactor's checklist item 1" "$item1"
report "$name"

# 3. The refactor leaf runs, after each transform, the suites affected-suites.sh prints when
#    fed refactor-touched.sh's output — the numbered item that says "after each transform",
#    read on its own through numbered_item.
name="develop-refactor runs affected-suites.sh fed refactor-touched.sh's output after each transform"
problems=()
refactor="$("$DEVELOP" refactor "$work/spec.md" 'QWIXTLE step' 'make test' 'src/zorblat.sh' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh refactor exited $?")
after_each="$(plain <<< "$refactor" | numbered_item 'after each transform')"
if [[ -z "$after_each" ]]; then
  problems+=("develop-refactor's prompt has no numbered item saying what runs after each transform")
fi
runs_affected "develop-refactor's after-each-transform item" "$after_each"
if ! grep -qF 'refactor-touched.sh' <<< "$after_each"; then
  problems+=("develop-refactor's after-each-transform item never feeds affected-suites.sh refactor-touched.sh's output")
fi
report "$name"

# 4. The green leaf and its verifier run the fast command plus the affected suites
#    (criterion 4): each prompt names detect-test-command.sh's `--tier fast` and tells its
#    leaf to run what affected-suites.sh prints, and neither still tells it to run, or keep
#    green, the full suite.
name="develop-green and verify-green name the fast command plus the affected suites, not the full suite"
problems=()
green="$("$DEVELOP" green "$work/spec.md" 'QWIXTLE step' 'make test' 'tests/zorblat.test.sh' 'zorblat case' 'make unit' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh green exited $?")
verify_green="$("$VERIFY" --fast-cmd 'make unit' green "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh green exited $?")
runs_fast_plus_affected develop-green "$green"
runs_fast_plus_affected verify-green "$verify_green"
report "$name"

# 5. The green leaf's two runs go through timed-test-run.sh (#373), which is what leaves a
#    `test-run` mark in the log. The wrapper has to be named at a path the leaf can run —
#    a leaf works in the target repository, where the bare name resolves to nothing — and
#    each run has to name its tier, since the mark's `tier=` key is the wrapper's first
#    argument and is what every later reader groups by. Read off case 4's `green`, the same
#    prompt built from the same arguments, rather than building it a second time.
name="develop-green runs the fast command and the affected suites through timed-test-run.sh, under tiers fast and affected"
problems=()
timed_through develop-green "$green" fast affected
report "$name"

# 6. The developer prompts other than green time their runs the same way (#373): red and
#    refactor run the suites affected-suites.sh prints, so tier `affected`; revise and
#    reconcile run the whole test command, so tier `all` — the tier word
#    detect-test-command.sh already uses for it. Red's and refactor's prompts are the ones
#    cases 1 and 3 built, read again rather than built a second time.
name="develop-red, develop-refactor, develop-revise and develop-reconcile run their test commands through timed-test-run.sh, each naming its tier"
problems=()
printf 'the verifier objected to the fixture path\n' > "$work/reason.md"
revise="$("$DEVELOP" revise red "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise exited $?")
reconcile="$("$DEVELOP" reconcile "$work/spec.md" 'QWIXTLE step' 'make test' 'tdd/1-zorblat' 'abc1234' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh reconcile exited $?")
timed_through develop-red "$red" affected
timed_through develop-refactor "$refactor" affected
timed_through develop-revise "$revise" all
timed_through develop-reconcile "$reconcile" all
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

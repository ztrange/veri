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
source "$HERE/lib/harness.sh"
DEVELOP="$HERE/../build-develop-prompt.sh"
VERIFY="$HERE/../build-verify-prompt.sh"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

runs_affected() {
  local label="$1" prompt="$2" named
  named="$(grep -E 'affected-suites\.sh' <<< "$(plain <<< "$prompt")")"
  if ! grep -qE '\brun' <<< "$named"; then
    problems+=("$label's prompt never tells its leaf to run the suites affected-suites.sh prints")
  fi
}

runs_fast_plus_affected() {
  local label="$1" prompt="$2" folded
  folded="$(plain <<< "$prompt")"
  if ! grep -qF -- '--tier fast' <<< "$folded"; then
    problems+=("$label's prompt never names the fast command (detect-test-command.sh --tier fast)")
  fi
  runs_affected "$label" "$prompt"
  if grep -qE "run (the )?(project's )?full (test )?suite|full suite (is )?green" <<< "$folded"; then
    problems+=("$label's prompt still tells its leaf to run, or keep green, the full suite")
  fi
}

timed_through() {
  local label="$1" prompt="$2"; shift 2
  local runnable="" cand tier folded
  while read -r cand; do
    [[ -x "$cand" ]] && runnable="$cand"
  done < <(grep -oE '[^ `]*timed-test-run\.sh' <<< "$prompt")
  if [[ -z "$runnable" ]]; then
    problems+=("$label's prompt never names timed-test-run.sh at a path the leaf can run")
  fi
  folded="$(plain <<< "$prompt")"
  for tier in "$@"; do
    if ! grep -qE "timed-test-run\.sh $tier\b" <<< "$folded"; then
      problems+=("$label's prompt never tells its leaf to run through timed-test-run.sh under tier $tier")
    fi
  done
}

names_suite_runner() {
  local label="$1" prompt="$2"
  if ! plain <<< "$prompt" | grep -F 'run-suite.sh' > /dev/null; then
    problems+=("$label's prompt never names run-suite.sh, the invocation for running one suite")
  fi
  if plain <<< "$prompt" | grep -F 'convention like any other' > /dev/null; then
    problems+=("$label's prompt still leaves how to run one suite for the leaf to establish")
  fi
}

names_runner_fallback() {
  local label="$1" prompt="$2" item
  item="$(plain <<< "$prompt" | numbered_item 'run-suite\.sh')"
  if [[ -z "$item" ]]; then
    problems+=("$label's prompt has no numbered item naming run-suite.sh")
    return
  fi
  if ! grep -qE 'fall back' <<< "$item"; then
    problems+=("$label's prompt never tells its leaf what to run when the repository has no run-suite.sh")
  fi
}

numbered_item() {
  awk -v re="$1" '
    /^[0-9]+\. /{if (item ~ re) {printf "%s", lines; done=1; exit} item=""; lines=""}
    /^[0-9]+\. /||item!=""{item=item " " $0; lines=lines $0 "\n"}
    END{if (!done && item ~ re) printf "%s", lines}'
}

printf 'zorblat must return frob\n' > "$work/spec.md"

name="develop-red and verify-red name affected-suites.sh, not one hand-named suite, as what they run"
problems=()
red="$("$DEVELOP" red "$work/spec.md" 'QWIXTLE step' 'make test' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh red exited $?")
verify_red="$("$VERIFY" red "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh red exited $?")
runs_affected develop-red "$red"
runs_affected verify-red "$verify_red"
if grep -qE 'run the suite that holds the new case' <<< "$(plain <<< "$red")"; then
  problems+=("develop-red still tells its leaf to run the one suite that holds the new case")
fi
report "$name"

name="verify-refactor's checklist item 1 names affected-suites.sh, not the project's full test suite"
problems=()
verify_refactor="$("$VERIFY" --fast-cmd 'make unit' refactor "$work/spec.md" 'tests/zorblat.test.sh' 'abc1234' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh refactor exited $?")
item1="$(numbered_item '^ 1\. still green' <<< "$(plain <<< "$verify_refactor")")"
if [[ -z "$item1" ]]; then
  problems+=("verify-refactor's prompt has no checklist item 1 ('1. still green')")
fi
if grep -qF "the project's full test suite" <<< "$item1"; then
  problems+=("verify-refactor's checklist item 1 still says \"the project's full test suite\"")
fi
runs_affected "verify-refactor's checklist item 1" "$item1"
report "$name"

name="develop-refactor runs affected-suites.sh fed refactor-touched.sh's output after each transform"
problems=()
refactor="$("$DEVELOP" refactor "$work/spec.md" 'QWIXTLE step' 'make test' 'src/zorblat.sh' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh refactor exited $?")
after_each="$(numbered_item 'after each transform' <<< "$(plain <<< "$refactor")")"
if [[ -z "$after_each" ]]; then
  problems+=("develop-refactor's prompt has no numbered item saying what runs after each transform")
fi
runs_affected "develop-refactor's after-each-transform item" "$after_each"
if ! grep -qF 'refactor-touched.sh' <<< "$after_each"; then
  problems+=("develop-refactor's after-each-transform item never feeds affected-suites.sh refactor-touched.sh's output")
fi
report "$name"

name="develop-green and verify-green name the fast command plus the affected suites, not the full suite"
problems=()
green="$("$DEVELOP" green "$work/spec.md" 'QWIXTLE step' 'make test' 'tests/zorblat.test.sh' 'zorblat case' 'make unit' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh green exited $?")
verify_green="$("$VERIFY" --fast-cmd 'make unit' green "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh green exited $?")
runs_fast_plus_affected develop-green "$green"
runs_fast_plus_affected verify-green "$verify_green"
report "$name"

name="develop-green runs the fast command and the affected suites through timed-test-run.sh, under tiers fast and affected"
problems=()
timed_through develop-green "$green" fast affected
report "$name"

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

name="verify-red, verify-green, verify-refactor and verify-pin run their test commands through timed-test-run.sh, each naming its tier"
problems=()
verify_pin="$("$VERIFY" pin "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh pin exited $?")
timed_through verify-red "$verify_red" affected
timed_through verify-green "$verify_green" fast affected
timed_through verify-refactor "$verify_refactor" fast affected
timed_through verify-pin "$verify_pin" target
report "$name"

name="verify-green's check 1 runs the target test through timed-test-run.sh, under tier target"
problems=()
check1="$(numbered_item 'The target test passes' <<< "$verify_green")"
if [[ -z "$check1" ]]; then
  problems+=("verify-green's prompt has no numbered item saying the target test passes")
fi
timed_through "verify-green's check 1" "$check1" target
report "$name"

suite_running_prompts=(develop-red "$red" develop-green "$green" develop-refactor "$refactor")

probe_prompts() {
  local probe="$1" i
  local -n roster="$2"
  for ((i = 0; i < ${#roster[@]}; i += 2)); do
    "$probe" "${roster[i]}" "${roster[i + 1]}"
  done
}

name="every developer prompt that runs a suite names run-suite.sh as the single-suite invocation"
problems=()
probe_prompts names_suite_runner suite_running_prompts
report "$name"

name="every developer prompt that names run-suite.sh tells its leaf what to run when the repository has none"
problems=()
probe_prompts names_runner_fallback suite_running_prompts
report "$name"

verifier_prompts=(
  verify-red "$verify_red"
  verify-green "$verify_green"
  verify-refactor "$verify_refactor"
  verify-pin "$verify_pin"
)
name="every blind verifier prompt names run-suite.sh as the single-suite invocation"
problems=()
probe_prompts names_suite_runner verifier_prompts
report "$name"

name="every blind verifier prompt that names run-suite.sh tells its leaf what to run when the repository has none"
problems=()
probe_prompts names_runner_fallback verifier_prompts
report "$name"


name="the prompt probes give the same verdict on a matching and a non-matching prompt when the writer is preempted"
problems=()

verdict() {
  local problems=()
  runs_fast_plus_affected develop-green "$1"
  timed_through develop-green "$1" fast affected
  printf '%s\n' "${#problems[@]}" "${problems[@]}"
}

unpreempted="$(declare -f plain)"
eval "honest_plain${unpreempted#plain}"
matching="$green"   # case 4's prompt, which every probe above accepts
missing='a prompt that names none of it'
honest_match="$(verdict "$matching")"
honest_miss="$(verdict "$missing")"
plain() { honest_plain; return 141; }
preempted_match="$(verdict "$matching")"
preempted_miss="$(verdict "$missing")"
eval "$unpreempted"

if [[ "$honest_match" != 0 ]]; then
  problems+=("with the writer intact the probes already object to a matching prompt (${honest_match%%$'\n'*} problems), so a verdict that survives preemption would only be two wrong answers agreeing")
fi
if [[ "${honest_miss%%$'\n'*}" == 0 ]]; then
  problems+=("with the writer intact the probes accept a prompt that names none of it, so a verdict that survives preemption would prove nothing")
fi
if [[ "$preempted_match" != "$honest_match" ]]; then
  problems+=("a preempted writer changes the probes' verdict on a matching prompt: ${honest_match%%$'\n'*} problems become ${preempted_match%%$'\n'*}")
fi
if [[ "$preempted_miss" != "$honest_miss" ]]; then
  problems+=("a preempted writer changes the probes' verdict on a non-matching prompt: ${honest_miss%%$'\n'*} problems become ${preempted_miss%%$'\n'*}")
fi
report "$name"
finish

#!/usr/bin/env bash
# Tests for which test command each phase's prompt tells its leaf to run — the prompt
# templates under scripts/prompts/, as build-develop-prompt.sh and build-verify-prompt.sh
# assemble them.
#
# Contract under test:
#   the assembled develop-red and verify-red prompts each name affected-suites.sh as what
#   the leaf runs, and develop-red no longer tells its leaf to run the one suite that holds
#   the new case.
#
# Run: scripts/tests/prompt-test-tiers.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
DEVELOP="$HERE/../build-develop-prompt.sh"
VERIFY="$HERE/../build-verify-prompt.sh"

work="$(scratch_dir)"


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

never_timed_under() {
  local label="$1" prompt="$2" tier="$3"
  if grep -qE "timed-test-run\.sh $tier\b" <<< "$(plain <<< "$prompt")"; then
    problems+=("$label's prompt still tells its leaf to run through timed-test-run.sh under tier $tier")
  fi
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
  re="$1" awk '
    /^[0-9]+\. /{if (item ~ ENVIRON["re"]) {printf "%s", lines; done=1; exit} item=""; lines=""}
    /^[0-9]+\. /||item!=""{item=item " " $0; lines=lines $0 "\n"}
    END{if (!done && item ~ ENVIRON["re"]) printf "%s", lines}'
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

name="develop-red, develop-refactor and develop-reconcile run their test commands through timed-test-run.sh, each naming its tier"
problems=()
reconcile="$("$DEVELOP" reconcile "$work/spec.md" 'QWIXTLE step' 'make test' 'tdd/1-zorblat' 'abc1234' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh reconcile exited $?")
timed_through develop-red "$red" affected
timed_through develop-refactor "$refactor" affected
timed_through develop-reconcile "$reconcile" all
report "$name"

name="develop-revise redoing red runs the affected suites through timed-test-run.sh under tier affected, and names no all run"
problems=()
printf 'the verifier objected to the fixture path\n' > "$work/reason.md"
revise="$("$DEVELOP" revise red "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise red exited $?")
runs_affected "develop-revise red" "$revise"
timed_through "develop-revise red" "$revise" affected
never_timed_under "develop-revise red" "$revise" all
report "$name"

name="develop-revise redoing refactor runs the affected suites through timed-test-run.sh under tier affected, and names no all run"
problems=()
revise_refactor="$("$DEVELOP" revise refactor "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise refactor exited $?")
runs_affected "develop-revise refactor" "$revise_refactor"
timed_through "develop-revise refactor" "$revise_refactor" affected
never_timed_under "develop-revise refactor" "$revise_refactor" all
report "$name"

name="develop-revise redoing green runs the fast command and the affected suites through timed-test-run.sh under tiers fast then affected, and names no all run"
problems=()
revise_green="$("$DEVELOP" revise green "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise green exited $?")
timed_through "develop-revise green" "$revise_green" fast affected
folded_revise_green="$(plain <<< "$revise_green")"
fast_at="$(awk '/timed-test-run\.sh fast( |$)/ && !n {n=NR} END{print n}' <<< "$folded_revise_green")"
affected_at="$(awk '/timed-test-run\.sh affected( |$)/ && !n {n=NR} END{print n}' <<< "$folded_revise_green")"
if [[ "$fast_at" =~ ^[1-9][0-9]*$ && "$affected_at" =~ ^[1-9][0-9]*$ ]] && ((fast_at > affected_at)); then
  problems+=("develop-revise green's prompt names the affected run before the fast one")
fi
never_timed_under "develop-revise green" "$revise_green" all
report "$name"

name="develop-revise runs the tiers of the phase it redoes — affected for red and refactor, fast and affected for green — and no all run, for each of the three"
problems=()
revise_tiers=(red 'affected' green 'fast affected' refactor 'affected')
for ((i = 0; i < ${#revise_tiers[@]}; i += 2)); do
  phase="${revise_tiers[i]}"
  redo="$("$DEVELOP" revise "$phase" "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
    problems+=("build-develop-prompt.sh revise $phase exited $?")
  read -ra tiers <<< "${revise_tiers[i + 1]}"
  timed_through "develop-revise $phase" "$redo" "${tiers[@]}"
  never_timed_under "develop-revise $phase" "$redo" all
done
report "$name"

name="the rebase leaves — develop-rebase, develop-reconcile and verify-rebase — still run the full test command under tier all"
problems=()
rebase="$("$DEVELOP" rebase "$work/spec.md" 'QWIXTLE step' 'make test' 'abc1234' 'def5678' 'src/zorblat.sh' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh rebase exited $?")
verify_rebase="$("$VERIFY" rebase "$work/spec.md" 'abc1234' 'def5678' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh rebase exited $?")
timed_through develop-rebase "$rebase" all
timed_through develop-reconcile "$reconcile" all
timed_through verify-rebase "$verify_rebase" all
for leaf in develop-rebase develop-reconcile; do
  [[ "$leaf" == develop-rebase ]] && redo="$rebase" || redo="$reconcile"
  if ! grep -qF "timed-test-run.sh all '' make test" <<< "$(plain <<< "$redo")"; then
    problems+=("$leaf's prompt never runs the full test command, make test, under tier all")
  fi
done
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

probe_tally() {
  local problems=()
  runs_fast_plus_affected develop-green "$1"
  timed_through develop-green "$1" fast affected
  printf '%s\n' "${#problems[@]}" "${problems[@]}"
}

unpreempted="$(declare -f plain)"
eval "honest_plain${unpreempted#plain}"
matching="$green"   # case 4's prompt, which every probe above accepts
missing='a prompt that names none of it'
honest_match="$(probe_tally "$matching")"
honest_miss="$(probe_tally "$missing")"
eval 'plain() { honest_plain; return 141; }'
preempted_match="$(probe_tally "$matching")"
preempted_miss="$(probe_tally "$missing")"
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

name="#1037: numbered_item given 'run-suite\\.sh' selects '2. run-suite.sh', not '1. run-suiteXsh'"
expect_eq "$name" "2. run-suite.sh" "$(printf '1. run-suiteXsh\n2. run-suite.sh\n' | numbered_item 'run-suite\.sh')"
finish

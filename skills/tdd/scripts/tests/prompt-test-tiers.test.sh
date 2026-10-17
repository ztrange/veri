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
    BEGIN{re=ENVIRON["re"]}
    /^[0-9]+\. /{if (item ~ re) {printf "%s", lines; done=1; exit} item=""; lines=""}
    /^[0-9]+\. /||item!=""{item=item " " $0; lines=lines $0 "\n"}
    END{if (!done && item ~ re) printf "%s", lines}'
}

printf 'zorblat must return frob\n' > "$work/spec.md"

problems=()
red="$("$DEVELOP" red "$work/spec.md" 'QWIXTLE step' 'make test' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh red exited $?")
verify_red="$("$VERIFY" red "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh red exited $?")
verify_refactor="$("$VERIFY" --fast-cmd 'make unit' refactor "$work/spec.md" 'tests/zorblat.test.sh' 'abc1234' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh refactor exited $?")
refactor="$("$DEVELOP" refactor "$work/spec.md" 'QWIXTLE step' 'make test' 'src/zorblat.sh' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh refactor exited $?")
green="$("$DEVELOP" green "$work/spec.md" 'QWIXTLE step' 'make test' 'tests/zorblat.test.sh' 'zorblat case' 'make unit' 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh green exited $?")
verify_green="$("$VERIFY" --fast-cmd 'make unit' green "$work/spec.md" 'tests/zorblat.test.sh' 'zorblat case' 2>/dev/null)" ||
  problems+=("build-verify-prompt.sh green exited $?")
printf 'the verifier objected to the fixture path\n' > "$work/reason.md"
revise="$("$DEVELOP" revise red "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise red exited $?")
revise_refactor="$("$DEVELOP" revise refactor "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise refactor exited $?")
revise_green="$("$DEVELOP" revise green "$work/spec.md" 'QWIXTLE step' 'make test' "$work/reason.md" 2>/dev/null)" ||
  problems+=("build-develop-prompt.sh revise green exited $?")

finish

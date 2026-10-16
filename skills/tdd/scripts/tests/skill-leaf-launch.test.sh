#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md launches a leaf, read as text.
#
# Contract under test:
#   5. Every launch line that reaches the verifier — by naming `verify.sh` or the verdict
#      launcher `run-verdict.sh` that execs it — names `supervise.sh` too.
#   7. Every verifier launch invokes the verdict launcher `run-verdict.sh` and inlines no
#      `bash -c` command string.
#   8. The document states in ONE place how the step's title reaches a command line, and
#      every fenced command carrying `<STEP>` follows that rule.
#   9. Every documented command line that passes a FRAGMENT of the step's title — the
#      `tick-ledger.sh`, `clear-refactor-pending.sh` and `tick-issue-criterion.sh` calls —
#      follows that same rule, read over the whole document, prose included.
#  10. That one rule says the title reaches a command line as data rather than hand-typed in
#      double quotes, and names every script the launch lines read it through.
#  11. Every line that builds the revise prompt with `build-develop-prompt.sh revise` hands
#      it the run's fast command, `'<fast-cmd>'`.
#
# Run: scripts/tests/skill-leaf-launch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

launcher="supervise.sh"
verifier="verify.sh"

verdict_launcher="run-verdict.sh"
verdict_leaf="verdict-"

step_ph="<STEP>"
double_quoted_step="\"$step_ph\""
single_quoted_step="'$step_ph'"

fragment_ph="<[^<>]*substring[^<>]*>"
double_quoted_fragment="\"$fragment_ph\""
single_quoted_fragment="'$fragment_ph'"

declare -A EXEMPT=(
)


source "$HERE/lib/harness.sh"
source "$HERE/lib/fenced-lines.sh"

fault() {
  faults="${faults:+$faults, and }$1"
}

faulted() {
  [[ -z "$faults" ]] ||
    problems+=("$skill_md:$1 $faults: $2")
}

read_quoted_lines() {
  local lines="$1" noun="$2" ph="$3" single="$4" double="$5"
  local lineno text
  while IFS=$'\t' read -r lineno text; do
    [[ -n "${EXEMPT[$skill_md:$lineno]:-}" ]] && continue
    faults=""
    if [[ "$text" =~ $single ]]; then
      fault "single-quotes $noun"
    elif [[ "$(sed -E "s|$double||g" <<< "$text")" =~ $ph ]]; then
      fault "carries $noun outside double quotes"
    fi
    faulted "$lineno" "$text"
  done <<< "$lines"
}

unreadable() {
  problems+=("$skill_md has no $1 — $2 could not be read")
}

lowered() {
  tr '[:upper:]' '[:lower:]'
}

name_re() {
  local out="" n
  for n in "$@"; do out+="|${n//./\\.}"; done
  printf '%s' "${out#|}"
}

launch_lines() {
  fenced_lines "$skill_path" "$(name_re "$launcher" "$verifier" "$verdict_launcher")"
}

finish

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



finish

#!/usr/bin/env bash
# Unit tests for the guard suites that read a scanner through `done < <(…)` — what each reports
# when its scanner fails.
#
# Contract under test:
#   no-recipe-unit-tier.test.sh, run as a
#   scratch copy over a clean scratch tree, passes with its grep scanner intact, and fails,
#   printing the scanner's exit status 2, when only that scanner's grep over the scratch tree
#   exits 2 — its planted-fixture cases, scanning elsewhere, keep a working grep. Every guard's
#   scanner-failure line names that guard by its own file name, `<guard>: …`.
#
# Run: skills/tdd/scripts/tests/scanner-status-guards.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

TESTS_DIR='skills/tdd/scripts/tests'
SCANNED='scanned.test.sh'
REAL_GREP="$(command -v grep)"

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

names_itself() {  # <guard> <scanned token> <output>: one line names the guard, then the scanned file and the status
  local line
  while IFS= read -r line; do
    [[ "$line" == *"$1: "*"$2"*'exit status 2'* ]] && return 0
  done <<< "$3"
  return 1
}

problems=()
name="no-recipe-unit-tier.test.sh passes over a clean scratch tree, and fails naming the suite and the scanner's exit status 2 when only the grep it reads through done < <(…) over that tree exits 2, the failure line naming the guard by its own file name (#1648)"

check_guard() {
  local guard="$1" scan_args="$2" token="$3" tree guard_out guard_code
  tree="$(scratch_dir)"
  mkdir -p "$tree/$TESTS_DIR/lib" "$tree/shim"
  cp "$HERE/lib/"*.sh "$tree/$TESTS_DIR/lib/"
  cp "$HERE/$guard" "$tree/$TESTS_DIR/$guard"
  chmod 755 "$tree/$TESTS_DIR/$guard"
  printf '%s\n' '#!/usr/bin/env bash' 'echo "0 passed, 0 failed"' 'wc -l /dev/null' > "$tree/$TESTS_DIR/$SCANNED"
  printf 'test:\n\t%s\n' "$TESTS_DIR/$SCANNED" > "$tree/Makefile"
  printf '#!/bin/sh\ncase "$PWD/ $*" in "%s/ %s "*|*" %s "*"%s/"*) exit 2 ;; esac\nexec "%s" "$@"\n' \
    "$tree" "$scan_args" "$scan_args" "$tree" "$REAL_GREP" > "$tree/shim/grep"
  chmod 755 "$tree/shim/grep"

  guard_out="$("$tree/$TESTS_DIR/$guard" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" == 0 ]] ||
    problems+=("want $guard to pass over the clean scratch tree with its scanner intact; it exited $guard_code and said: $(flat "$guard_out")")

  guard_out="$(PATH="$tree/shim:$PATH" "$tree/$TESTS_DIR/$guard" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want $guard to fail when its scanner, grep $scan_args over the scratch tree, exits 2; it exited 0 and said: $(flat "$guard_out")")
  grep -F -- "$token" <<< "$guard_out" > /dev/null ||
    problems+=("no line of $guard's output names $token; it said: $(flat "$guard_out")")
  grep -F -- 'exit status 2' <<< "$guard_out" > /dev/null ||
    problems+=("no line of $guard's output names the scanner's exit status 2; it said: $(flat "$guard_out")")
  names_itself "$guard" "$token" "$guard_out" ||
    problems+=("no line of $guard's output names the guard itself, as '$guard: ', beside $token and the scanner's exit status 2; it said: $(flat "$guard_out")")
}

CASES=(  # guard | the scanner's leading grep arguments | token its output must name besides the status
  "no-recipe-unit-tier.test.sh|-nE|$SCANNED"
)

for entry in "${CASES[@]}"; do
  IFS='|' read -r guard scan_args token <<< "$entry"
  check_guard "$guard" "$scan_args" "$token"
done

report "$name"

finish

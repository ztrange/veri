#!/usr/bin/env bash
# Unit tests for the guard suites that read a scanner through `done < <(…)` — what each reports
# when its scanner fails.
#
# Contract under test:
#   no-awk-v-patterns.test.sh, no-docs-reads.test.sh and no-job-spec-kills.test.sh, run as a
#   scratch copy over a clean scratch tree, pass with their grep scanner intact, and fail,
#   printing the scanner's exit status 2, when only that scanner's grep over the scratch tree
#   exits 2 — their planted-fixture cases, scanning elsewhere, keep a working grep. Every guard's
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

CASES=(  # guard | the scanner's leading grep arguments | token its output must name besides the status
  "no-awk-v-patterns.test.sh|-n awk|$SCANNED"
  "no-docs-reads.test.sh|-nE|$SCANNED"
  'no-job-spec-kills.test.sh|-rInE --|skills'
)

problems=()
name="no-awk-v-patterns.test.sh, no-docs-reads.test.sh and no-job-spec-kills.test.sh each pass over a clean scratch tree, and fail naming the suite and the scanner's exit status 2 when only the grep they read through done < <(…) over that tree exits 2, the failure line naming the guard by its own file name (#1648)"

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

for entry in "${CASES[@]}"; do
  IFS='|' read -r guard scan_args token <<< "$entry"
  check_guard "$guard" "$scan_args" "$token"
done

report "$name"

CASES=(
  "no-recipe-unit-tier.test.sh|-nE|$SCANNED"
  "no-sigpipe-pipelines.test.sh|-nE|$SCANNED"
  "no-size-assertion.test.sh|-nE|$SCANNED"
)

problems=()
name="no-recipe-unit-tier.test.sh, no-sigpipe-pipelines.test.sh and no-size-assertion.test.sh each pass over a clean scratch tree, and fail naming the suite and the scanner's exit status 2 when only the grep they read through done < <(…) over that tree exits 2, the failure line naming the guard by its own file name (#1648)"

for entry in "${CASES[@]}"; do
  IFS='|' read -r guard scan_args token <<< "$entry"
  check_guard "$guard" "$scan_args" "$token"
done

report "$name"

problems=()
name="scratch-copy-libs.test.sh passes over a clean scratch tree, and fails naming the file it scanned and the scanner's exit status 2 when only the scanner they read through done < <(…) exits 2, the failure line naming the guard by its own file name (#1648)"

check_scanner() {
  local guard="$1" shim_cmd="$2" shim_case="$3" token="$4" tree guard_out guard_code
  tree="$(scratch_dir)"
  mkdir -p "$tree/$TESTS_DIR/lib" "$tree/shim"
  cp "$HERE/lib/"*.sh "$tree/$TESTS_DIR/lib/"
  cp "$HERE/$guard" "$tree/$TESTS_DIR/$guard"
  chmod 755 "$tree/$TESTS_DIR/$guard"
  case "$guard" in
    scratch-copy-libs.test.sh)
      printf '%s\n' '#!/usr/bin/env bash' 'source "$HERE/lib/verdict.sh"' > "$tree/$TESTS_DIR/planted.test.sh"
      printf '%s\n' '#!/usr/bin/env bash' "GUARD='skills/tdd/scripts/tests/planted.test.sh'" \
        'cp "$HERE/lib/harness.sh" "$tree/lib/"' 'cp "$HERE/lib/verdict.sh" "$tree/lib/"' > "$tree/$TESTS_DIR/plants.test.sh" ;;
  esac
  local entry
  for entry in "$HERE"/../*; do
    [[ "$entry" == "$HERE" ]] || ln -s "$entry" "$tree/skills/tdd/scripts/${entry##*/}"
  done
  printf '#!/bin/sh\ncase "$*" in %s) : > "%s"; exit 2 ;; esac\nexec "%s" "$@"\n' \
    "$shim_case" "$tree/fired" "$(command -v "$shim_cmd")" > "$tree/shim/$shim_cmd"
  chmod 755 "$tree/shim/$shim_cmd"

  guard_out="$("$tree/$TESTS_DIR/$guard" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" == 0 ]] ||
    problems+=("want $guard to pass over the clean scratch tree with its scanner intact; it exited $guard_code and said: $(flat "$guard_out")")

  guard_out="$(PATH="$tree/shim:$PATH" "$tree/$TESTS_DIR/$guard" 2>&1)" && guard_code=0 || guard_code=$?
  [[ -e "$tree/fired" ]] ||
    problems+=("want $guard to run its $shim_cmd scanner as $shim_case; the shim never matched it, so this case tested nothing")
  [[ "$guard_code" != 0 ]] ||
    problems+=("want $guard to fail when its $shim_cmd scanner exits 2; it exited 0 and said: $(flat "$guard_out")")
  grep -F -- "$token" <<< "$guard_out" > /dev/null ||
    problems+=("no line of $guard's output names $token; it said: $(flat "$guard_out")")
  grep -F -- 'exit status 2' <<< "$guard_out" > /dev/null ||
    problems+=("no line of $guard's output names the scanner's exit status 2; it said: $(flat "$guard_out")")
  names_itself "$guard" "$token" "$guard_out" ||
    problems+=("no line of $guard's output names the guard itself, as '$guard: ', beside $token and the scanner's exit status 2; it said: $(flat "$guard_out")")
}

check_scanner scratch-copy-libs.test.sh sed "'-nE '*'/planted.test.sh'" planted.test.sh

report "$name"

finish

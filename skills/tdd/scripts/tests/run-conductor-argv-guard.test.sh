#!/usr/bin/env bash
# Unit test for run-conductor.test.sh — the suite that pins how a conductor is launched.
# Its subject is what that suite reports when the code under it regresses.
#
# Contract under test:
#   Put back the launch that hands the procedure to `claude -p` as an argv element whose
#   first character is a dash, and run-conductor.test.sh's case 4, the case that pins the
#   procedure reaching the binary whole, fails by name. Leave the launch as it is and the
#   same case, in the same kind of tree, passes.
#
# Run: skills/tdd/scripts/tests/run-conductor-argv-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SKILL_DIR='skills/tdd'
SCRIPTS_DIR="$SKILL_DIR/scripts"
TESTS_DIR="$SCRIPTS_DIR/tests"

SUBJECT_NAME='run-conductor.test.sh'
SUBJECT_PATH="$ROOT/$TESTS_DIR/$SUBJECT_NAME"
SCRIPT_NAME='run-conductor.sh'
SCRIPT_PATH="$ROOT/$SCRIPTS_DIR/$SCRIPT_NAME"
SKILL_NAME='SKILL.md'

CASE4_NAME='a frontmatter-fenced procedure launches and reaches the binary whole'

ARGV_LAUNCH='s#^printf .* | \(.*\) -p \\$#\1 -p "$prompt" \\#'


source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

trees=()

run_case4() {
  local arm="$1" rewrite="$2" tree script cut out code
  tree="$(scratch_dir)" || { problems+=("could not make the $arm arm's scratch tree"); return; }
  trees+=("$tree")
  mkdir -p "$tree/$TESTS_DIR"
  cp "$SUBJECT_PATH" "$tree/$TESTS_DIR/$SUBJECT_NAME"
  mkdir -p "$tree/$TESTS_DIR/lib" && cp "$HERE/lib/harness.sh" "$tree/$TESTS_DIR/lib/"
  cp "$ROOT/$SKILL_DIR/$SKILL_NAME" "$tree/$SKILL_DIR/$SKILL_NAME"
  mkdir -p "$tree/$SCRIPTS_DIR/lib" && cp "$ROOT/$SCRIPTS_DIR/lib/exit-contract.sh" "$tree/$SCRIPTS_DIR/lib/"
  script="$tree/$SCRIPTS_DIR/$SCRIPT_NAME"
  if [[ -n "$rewrite" ]]; then sed "$rewrite" "$SCRIPT_PATH" > "$script"; else cp "$SCRIPT_PATH" "$script"; fi
  chmod 755 "$tree/$TESTS_DIR/$SUBJECT_NAME" "$script"
  git -C "$tree" init -q && git -C "$tree" add -A &&
    git -C "$tree" -c user.name=guard -c user.email=guard@example.invalid commit -qm tree ||
    problems+=("could not commit the $arm arm's scratch tree, so the subject had no committed skill to launch")
  cut="$tree/$TESTS_DIR/case4-only.test.sh"
  awk '/^name=/ {skip = ++n != 4} !skip' \
    "$tree/$TESTS_DIR/$SUBJECT_NAME" > "$cut"
  printf '%s\n' 'echo "----"' 'echo "${pass:-0} passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$cut"
  chmod +x "$cut"
  grep -qF "name=\"$CASE4_NAME\"" "$cut" ||
    problems+=("case 4 could not be cut out of $SUBJECT_NAME in the $arm arm: no line names '$CASE4_NAME'")
  out="$("$cut" 2>&1)" && code=0 || code=$?
  printf -v "out_$arm" '%s' "$out"
  printf -v "code_$arm" '%s' "$code"
  printf -v "script_$arm" '%s' "$script"
}

probe_sabotage_is_real() {
  cmp -s "$SCRIPT_PATH" "$script_planted" &&
    problems+=("the rewrite left $SCRIPT_NAME byte-identical, so the argv launch was never put back and the planted arm asks nothing")
  return 0
}

probe_planted_arm_fails_case4() {
  [[ "$code_planted" != 0 ]] ||
    problems+=("with the procedure back on argv, case 4 of $SUBJECT_NAME exited 0: a launch no real binary would accept reads as a checked one. It said: $(flat "$out_planted")")
  [[ "$out_planted" == *"FAIL - $CASE4_NAME"* ]] ||
    problems+=("with the procedure back on argv, case 4 of $SUBJECT_NAME did not fail by name. It said: $(flat "$out_planted")")
  [[ "$(tail -n 1 <<< "$out_planted")" == "0 passed, 1 failed" ]] ||
    problems+=("with the procedure back on argv, case 4's count line was not '0 passed, 1 failed': $(flat "$(tail -n 1 <<< "$out_planted")")")
}

probe_untouched_arm_passes_case4() {
  [[ "$code_untouched" == 0 && "$(tail -n 1 <<< "$out_untouched")" == "1 passed, 0 failed" ]] ||
    problems+=("with the launch untouched, case 4 of $SUBJECT_NAME did not pass in the same kind of tree (exit $code_untouched), so a red in the planted arm says nothing about the plant. It said: $(flat "$out_untouched")")
}

name="run-conductor.test.sh's case 4 fails when the procedure is passed as an argv element beginning with a dash, and passes when it is not"
problems=()
out_planted="" code_planted="" script_planted="" out_untouched="" code_untouched=""
run_case4 planted "$ARGV_LAUNCH"
run_case4 untouched ''
probe_sabotage_is_real
probe_planted_arm_fails_case4
probe_untouched_arm_passes_case4
report "$name"

finish

#!/usr/bin/env bash
# Unit test for run-conductor.test.sh — the suite that pins how a conductor is launched.
# Like docs-read-guard-plant.test.sh and count-line-guard.test.sh this suite has no script
# as its subject: its subject is what another suite reports when the code under it regresses.
# Zero-dependency plain-shell asserts, same idiom as docs-read-guard-plant.test.sh.
#
# Why this exists (issue #221): run-conductor.sh passed the procedure as the argument to
# `-p`, and SKILL.md's first line is the YAML frontmatter fence `---`. A real `claude` parses
# a leading-dash argument as an option and dies on `unknown option '---` before a conductor
# exists — yet run-conductor.test.sh was green on that script for as long as it existed,
# because the stub it drives recorded its argv and never parsed it. The seam that makes the
# launch testable with no model is the same seam that hid the one thing the real binary does
# differently, and a stub that accepts an argv the binary would reject makes every
# argv-shape bug invisible.
#
# Contract under test:
#   Put back the launch that #221 fixed — the procedure handed to `claude -p` as an argv
#   element whose first character is a dash — and run-conductor.test.sh's case 4, the case
#   that pins the procedure reaching the binary whole, fails by name. Leave the launch as it
#   is and the same case, in the same kind of tree, passes.
#
# The subject is run rather than read: the issue names two fixes that both satisfy the
# criterion — a stub strict enough to refuse the argv, or an assertion on what reaches the
# binary's stdin — so a check that read the suite for one of them would pass that one and
# fail the other. What is asked instead is what both have in common: case 4 goes red.
#
# So each arm stands up a scratch tree holding the suite, the procedure and run-conductor.sh —
# rewritten back to the argv form in one arm, untouched in the other — commits it as a git
# repository, cuts case 4 out of the suite the way run-conductor.test.sh's own case 21 does,
# and runs that. The tree is a repository, and the planted script is committed there, because
# the suite builds every launch from the tree's committed skill (`tree_clone`, #258): in a
# plain directory half its cases die on `not a git repository`, which is how this guard went
# vacuous — it asked only that SOME case failed, and a tree the suite could not use answered
# that on its own, bug or no bug. That is also why the untouched arm exists: it is what says
# a red in the planted arm was caused by the plant. `probe_sabotage_is_real` asserts the
# rewrite actually changed the file, because a `sed` whose pattern had drifted off the script
# would leave the planted arm reporting on an unsabotaged launch.
#
# Run: skills/tdd/scripts/tests/run-conductor-argv-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The three paths the scratch tree reproduces, relative to the root, because the subject
# reaches for the script and the procedure by walking up from wherever it stands.
SKILL_DIR='skills/tdd'
SCRIPTS_DIR="$SKILL_DIR/scripts"
TESTS_DIR="$SCRIPTS_DIR/tests"

SUBJECT_NAME='run-conductor.test.sh'
SUBJECT_PATH="$ROOT/$TESTS_DIR/$SUBJECT_NAME"
SCRIPT_NAME='run-conductor.sh'
SCRIPT_PATH="$ROOT/$SCRIPTS_DIR/$SCRIPT_NAME"
SKILL_NAME='SKILL.md'

# Case 4 of the subject, by the name it reports under: the one case whose criterion #221 is.
CASE4_NAME='a frontmatter-fenced procedure launches and reaches the binary whole'

# The regression, as the one `sed` rewrite that causes it: the launch stops piping the
# procedure into `claude -p` and hands it over as the argument instead — the exact line #221
# replaced, put back. Delimited with `#` because the line it matches contains both `%` (the
# printf format) and `/` (nothing here, but the format's siblings elsewhere do).
ARGV_LAUNCH='s#^printf .* | \(.*\) -p \\$#\1 -p "$prompt" \\#'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which way the subject failed to notice rather than just that it did.
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

# flat <text> — one line of it, for a failure message.
flat() { printf '%s' "$1" | tr '\n' '/'; }

trees=()
trap 'rm -rf "${trees[@]+"${trees[@]}"}"' EXIT

# run_case4 <arm> <sed-rewrite|''> — stand up one arm's tree and run case 4 in it, leaving the
# run's output in `out_<arm>`, its status in `code_<arm>` and the script copy's path in
# `script_<arm>`. An empty rewrite copies run-conductor.sh untouched. The suite, the procedure
# and the script are committed before anything runs, for the reason in the header. Case 4 is
# cut the way run-conductor.test.sh's case 21 cuts it: the preamble, case 4 and a count line,
# so the subject's own case is what is asked, as written, and nothing else in it.
run_case4() {
  local arm="$1" rewrite="$2" tree script cut out code
  tree="$(mktemp -d)" || { problems+=("could not make the $arm arm's scratch tree"); return; }
  trees+=("$tree")
  mkdir -p "$tree/$TESTS_DIR"
  cp "$SUBJECT_PATH" "$tree/$TESTS_DIR/$SUBJECT_NAME"
  cp "$ROOT/$SKILL_DIR/$SKILL_NAME" "$tree/$SKILL_DIR/$SKILL_NAME"
  script="$tree/$SCRIPTS_DIR/$SCRIPT_NAME"
  if [[ -n "$rewrite" ]]; then sed "$rewrite" "$SCRIPT_PATH" > "$script"; else cp "$SCRIPT_PATH" "$script"; fi
  chmod 755 "$tree/$TESTS_DIR/$SUBJECT_NAME" "$script"
  git -C "$tree" init -q && git -C "$tree" add -A &&
    git -C "$tree" -c user.name=guard -c user.email=guard@example.invalid commit -qm tree ||
    problems+=("could not commit the $arm arm's scratch tree, so the subject had no committed skill to launch")
  cut="$tree/$TESTS_DIR/case4-only.test.sh"
  awk '/^# 1\. / {skip=1} /^# 4\. / {skip=0} /^# 5\. / {skip=1} !skip' \
    "$tree/$TESTS_DIR/$SUBJECT_NAME" > "$cut"
  printf '%s\n' 'echo "----"' 'echo "$pass passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$cut"
  chmod +x "$cut"
  grep -qF "name=\"$CASE4_NAME\"" "$cut" ||
    problems+=("case 4 could not be cut out of $SUBJECT_NAME in the $arm arm: no line names '$CASE4_NAME'")
  out="$("$cut" 2>&1)" && code=0 || code=$?
  printf -v "out_$arm" '%s' "$out"
  printf -v "code_$arm" '%s' "$code"
  printf -v "script_$arm" '%s' "$script"
}

# probe_sabotage_is_real — the planted arm's script differs from the real one.
probe_sabotage_is_real() {
  cmp -s "$SCRIPT_PATH" "$script_planted" &&
    problems+=("the rewrite left $SCRIPT_NAME byte-identical, so the argv launch was never put back and the planted arm asks nothing")
  return 0
}

# probe_planted_arm_fails_case4 — the criterion: with the procedure back on argv, case 4 fails,
# by name, and the run's count line says so.
probe_planted_arm_fails_case4() {
  [[ "$code_planted" != 0 ]] ||
    problems+=("with the procedure back on argv, case 4 of $SUBJECT_NAME exited 0: a launch no real binary would accept reads as a checked one. It said: $(flat "$out_planted")")
  [[ "$out_planted" == *"FAIL - $CASE4_NAME"* ]] ||
    problems+=("with the procedure back on argv, case 4 of $SUBJECT_NAME did not fail by name. It said: $(flat "$out_planted")")
  [[ "$(tail -n 1 <<< "$out_planted")" == "0 passed, 1 failed" ]] ||
    problems+=("with the procedure back on argv, case 4's count line was not '0 passed, 1 failed': $(flat "$(tail -n 1 <<< "$out_planted")")")
}

# probe_untouched_arm_passes_case4 — the control: the same tree with the real launch passes the
# same case, so the planted arm's red was the plant's doing and not the tree's.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

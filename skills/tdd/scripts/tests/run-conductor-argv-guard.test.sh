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
#   element whose first character is a dash — and run-conductor.test.sh fails, both in the
#   status a runner reads and in the count line `make test` reads.
#
# The subject is run rather than read: the issue names two fixes that both satisfy the
# criterion — a stub strict enough to refuse the argv, or an assertion on what reaches the
# binary's stdin — so a check that read the suite for one of them would pass that one and
# fail the other. What is asked instead is the only thing both have in common, which is that
# the suite goes red.
#
# So run-conductor.sh is copied into a scratch tree with its launch line rewritten back to
# the argv form, the subject is copied beside it, and the subject is run there. The subject
# resolves the script one directory up from itself and the procedure two, so the copy only
# behaves like the original if it stands in the same shape of tree. `probe_sabotage_is_real`
# asserts the rewrite actually changed the file, because a `sed` whose pattern had drifted
# off the script would leave the probes below reporting on an unsabotaged launch and the
# case would go green over the hole it exists to pin.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a run's
# output quoted inside an indented problem line stays one line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# plant_subject <sed edit> — stand the subject up in a scratch tree beside a copy of
# run-conductor.sh with that one line rewritten, leaving the tree's path in `tree`, the
# subject's copy in `subject_copy` and the script's in `script_copy`. The procedure goes in
# too, verbatim: it is what the launch carries, and its frontmatter fence is the whole point.
plant_subject() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to stand the subject up in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"
  subject_copy="$tree/$TESTS_DIR/$SUBJECT_NAME"
  script_copy="$tree/$SCRIPTS_DIR/$SCRIPT_NAME"
  cp "$SUBJECT_PATH" "$subject_copy"
  cp "$ROOT/$SKILL_DIR/$SKILL_NAME" "$tree/$SKILL_DIR/$SKILL_NAME"
  sed "$1" "$SCRIPT_PATH" > "$script_copy"
  chmod 755 "$subject_copy" "$script_copy"
}

# probe_sabotage_is_real — the premise the probes below rest on, asserted rather than
# assumed: the rewrite matched a line and the copy differs from the original.
probe_sabotage_is_real() {
  cmp -s "$SCRIPT_PATH" "$script_copy" &&
    problems+=("the rewrite left $SCRIPT_NAME byte-identical, so the argv launch was never put back and nothing below asks the criterion")
  return 0
}

# probe_fails_loudly — the criterion, asked of one run of the subject in the two ways a
# suite answers: the exit status a runner reads, and the count line `make test` reads. The
# count is asked for a non-zero failure tally rather than an exact one, because how many of
# the subject's cases notice an argv launch is not the criterion — that any of them does is.
probe_fails_loudly() {
  local out code count_line
  out="$("$subject_copy" 2>&1)" && code=0 || code=$?
  [[ "$code" != 0 ]] ||
    problems+=("with the procedure back on argv, $SUBJECT_NAME exited 0: a launch no real binary would accept reads as a checked one. It said: $(flat "$out")")
  count_line="$(tail -n 1 <<< "$out")"
  [[ "$count_line" =~ [1-9][0-9]*\ failed$ ]] ||
    problems+=("with the procedure back on argv, $SUBJECT_NAME counted no case as failed; its count line was: $(flat "$count_line")")
}

# 1. One criterion, one case: the suite fails when the procedure is an argv element whose
#    first character is a dash.
name="run-conductor.test.sh fails when the procedure is passed as an argv element beginning with a dash"
problems=()
tree=""
subject_copy=""
script_copy=""

if plant_subject "$ARGV_LAUNCH"; then
  probe_sabotage_is_real
  probe_fails_loudly
fi
[[ -z "$tree" ]] || rm -rf "$tree"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

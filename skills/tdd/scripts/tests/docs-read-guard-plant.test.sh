#!/usr/bin/env bash
# Unit tests for docs-read-guard.test.sh — the suite that pins the guard keeping the
# development lane out of the generated-documentation tree. Like count-line-guard.test.sh
# and hermetic-suites.test.sh this suite has no script as its subject: its subject is what
# another suite reports when the fixture its whole case rests on was not built.
# Zero-dependency plain-shell asserts, same idiom as count-line-guard.test.sh.
#
# Why this exists (issue #183): docs-read-guard.test.sh runs under `set -uo pipefail`
# without `-e`, and its `plant` ends in an assignment — the line number of the fixture's
# marked line, taken with `grep -n`. A fixture edit that renames the mark, or a plant_reader
# that stops writing its file, makes that grep come back non-zero, `plant` return non-zero,
# and the case's `if probe_guard_is_there && plant; then` skip all four probes. `report`
# then sees an empty `problems` array and counts a pass. The guard it exists to pin could be
# gone and the suite would still print `1 passed, 0 failed`, which is the one answer a guard
# suite must never be able to give.
#
# Contract under test:
#   When its plant fails after the scratch tree is made — the reader carries no line
#   matching the mark, or the reader fixture was never written — docs-read-guard.test.sh
#   fails, and says which premise broke. And with that plant intact it still discriminates:
#   it passes against the real no-docs-reads.test.sh and fails against a guard that always
#   passes, so the fix for the first half did not buy a loud failure with a blind pass.
#
# The subject is run rather than read: whether a skipped probe reaches `report` with nothing
# to say is a fact about what the suite does when it is run, and a check that read the file
# for an `if` of a particular shape would pass either of the two fixes the issue names and
# fail the other. So the subject is copied into a scratch tree through `sed`, with the one
# line that breaks the plant rewritten, and run there. `probe_sabotage_is_real` asserts the
# rewrite actually changed the file, because a `sed` whose pattern no longer matches would
# leave every probe below reporting on an unsabotaged suite.
#
# The scratch tree carries a stub guard at the path the subject looks for, so that the
# subject's own first probe — there is a guard suite, and it can be run — passes and the
# plant is reached. The stub always passes, which is the shape #183 was watched on: with the
# plant broken, the subject never runs it at all.
#
# Run: skills/tdd/scripts/tests/docs-read-guard-plant.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

TESTS_DIR='skills/tdd/scripts/tests'
GUARD_NAME='no-docs-reads.test.sh'

SUBJECT_NAME='docs-read-guard.test.sh'
SUBJECT_PATH="$ROOT/$TESTS_DIR/$SUBJECT_NAME"

pass=0 fail=0

source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

plant_subject() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to stand the subject up in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR/lib" && cp "$ROOT/$TESTS_DIR/lib/harness.sh" "$tree/$TESTS_DIR/lib/"
  subject_copy="$tree/$TESTS_DIR/$SUBJECT_NAME"
  sed "$1" "$SUBJECT_PATH" > "$subject_copy"
  chmod 755 "$subject_copy"

  cat > "$tree/$TESTS_DIR/$GUARD_NAME" <<'STUB'
#!/usr/bin/env bash
set -uo pipefail
echo "----"
echo "1 passed, 0 failed"
STUB
  chmod 755 "$tree/$TESTS_DIR/$GUARD_NAME"
}

probe_sabotage_is_real() {
  cmp -s "$SUBJECT_PATH" "$subject_copy" &&
    problems+=("$1 left $SUBJECT_NAME byte-identical, so its plant was never broken and nothing below asks the criterion")
  return 0
}

run_subject() {
  run_out="$("$subject_copy" 2>&1)" && run_code=0 || run_code=$?
}

probe_fails_loudly() {
  [[ "$run_code" != 0 ]] ||
    problems+=("with $1, $SUBJECT_NAME exited 0: a plant that never ran reads as a checked guard. It said: $(flat "$run_out")")
  local count_line
  count_line="$(tail -n 1 <<< "$run_out")"
  [[ "$count_line" == '0 passed, 1 failed' ]] ||
    problems+=("with $1, $SUBJECT_NAME did not count its one case as failed; its count line was: $(flat "$count_line")")
  grep -Eqi '^[[:space:]]+.*(plant|reader|mark)' <<< "$run_out" ||
    problems+=("with $1, $SUBJECT_NAME reported no problem line naming the broken premise, so its failure does not say what to fix. It said: $(flat "$run_out")")
}

name="docs-read-guard.test.sh fails and names the broken premise when its plant finds no marked line or never wrote the reader fixture"
problems=()
tree=""
subject_copy=""
run_out=""
run_code=0

while IFS='|' read -r edit_label edit; do
  [[ -n "$edit_label" ]] || continue
  if plant_subject "$edit"; then
    probe_sabotage_is_real "$edit_label"
    run_subject
    probe_fails_loudly "$edit_label"
  fi
  [[ -z "$tree" ]] || rm -rf "$tree"
  tree=""
done <<'SABOTAGES'
no marked line in the planted reader|s%"\$MARK" >> "\$reader_path"%"a-comment-that-is-not-the-mark" >> "\$reader_path"%
the reader fixture never written|s%^  plant_reader$%  : # sabotage: the reader fixture is never written%
SABOTAGES

report "$name"

probe_plant_is_intact() {
  cmp -s "$SUBJECT_PATH" "$subject_copy" ||
    problems+=("the copy in the scratch tree is not $SUBJECT_NAME byte for byte, so what it reports is not about the subject")
  return 0
}

probe_passes_against_the_real_guard() {
  local out code
  out="$("$SUBJECT_PATH" 2>&1)" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("against the real $GUARD_NAME with its plant intact, $SUBJECT_NAME exited $code; it said: $(flat "$out")")
  local count_line
  count_line="$(tail -n 1 <<< "$out")"
  [[ "$count_line" == '1 passed, 0 failed' ]] ||
    problems+=("against the real $GUARD_NAME with its plant intact, $SUBJECT_NAME did not count its one case as passed; its count line was: $(flat "$count_line")")
}

probe_fails_against_a_passing_stub() {
  [[ "$run_code" != 0 ]] ||
    problems+=("against a guard that always passes, $SUBJECT_NAME exited 0 with its plant intact: it is not asking the guard anything. It said: $(flat "$run_out")")
  local count_line
  count_line="$(tail -n 1 <<< "$run_out")"
  [[ "$count_line" == '0 passed, 1 failed' ]] ||
    problems+=("against a guard that always passes, $SUBJECT_NAME did not count its one case as failed; its count line was: $(flat "$count_line")")
}

name="docs-read-guard.test.sh with its plant intact passes against the real no-docs-reads.test.sh and fails against a guard that always passes"
problems=()
tree=""
subject_copy=""
run_out=""
run_code=0

probe_passes_against_the_real_guard
if plant_subject 's%^$%%'; then
  probe_plant_is_intact
  run_subject
  probe_fails_against_a_passing_stub
fi
[[ -z "$tree" ]] || rm -rf "$tree"
tree=""

report "$name"
echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# Where a suite lives, and so where the scratch tree puts both files: the subject resolves
# its own repo root four directories up from itself and looks for the guard under this path,
# so the copy only behaves like the original if it stands in the same shape of tree.
TESTS_DIR='skills/tdd/scripts/tests'
GUARD_NAME='no-docs-reads.test.sh'

# The subject twice, and neither name substitutes for the other: bare is what the scratch
# tree names its copy and what every failure message here says, absolute is what copying it
# into that tree needs. Built onto TESTS_DIR above rather than spelled out, so the directory
# a suite lives in is stated in one place.
SUBJECT_NAME='docs-read-guard.test.sh'
SUBJECT_PATH="$ROOT/$TESTS_DIR/$SUBJECT_NAME"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# plant_subject <sed edit> — stand the subject up in a scratch tree with that one line
# rewritten, leaving the tree's path in `tree` and the copy's in `subject_copy`. The stub
# guard beside it is what gets the subject past its own first probe; it always passes, so
# nothing in the run below depends on the real guard.
plant_subject() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to stand the subject up in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"
  subject_copy="$tree/$TESTS_DIR/$SUBJECT_NAME"
  sed "$1" "$SUBJECT_PATH" > "$subject_copy"
  chmod 755 "$subject_copy"

  cat > "$tree/$TESTS_DIR/$GUARD_NAME" <<'STUB'
#!/usr/bin/env bash
# A guard that checks nothing and says so in the only way a runner reads: it passes.
set -uo pipefail
echo "----"
echo "1 passed, 0 failed"
STUB
  chmod 755 "$tree/$TESTS_DIR/$GUARD_NAME"
}

# probe_sabotage_is_real — the premise every probe below rests on, asserted rather than
# assumed: the rewrite matched a line and the copy differs from the original. A `sed` whose
# pattern had drifted off the subject would leave the run below reporting on an unsabotaged
# suite, and the case would go green over the hole it exists to pin.
probe_sabotage_is_real() {
  cmp -s "$SUBJECT_PATH" "$subject_copy" &&
    problems+=("$1 left $SUBJECT_NAME byte-identical, so its plant was never broken and nothing below asks the criterion")
  return 0
}

# run_subject — run the sabotaged copy once, leaving what it said in `run_out` and how it
# exited in `run_code`. Taken on the spot with `&& … || …`, since this suite does not run
# under `set -e` and the subject is expected to fail.
run_subject() {
  run_out="$("$subject_copy" 2>&1)" && run_code=0 || run_code=$?
}

# probe_fails_loudly <what was broken> — the criterion, asked of the one run above in the
# three ways a suite answers: the exit status a runner reads, the count line `make test`
# reads, and the problem line a human reads. The third is the one #183 is about — a suite
# that failed without saying which premise broke would send the next author to the guard
# rather than to the fixture — and it asks only that some problem line name the plant, the
# reader or the mark, because which of the two fixes the issue offers is taken is not the
# criterion.
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

# 1. One criterion, one case: a plant that fails after the scratch tree is made fails the
#    case and names the premise. Both ways it can fail are probed, because they are one
#    criterion rather than two — the last line of `plant` is an assignment whose status is
#    the function's, and a missing mark and a missing fixture are the same non-zero coming
#    out of the same `grep`. A case that pinned only one of them would pass a fix that
#    special-cased it.
name="docs-read-guard.test.sh fails and names the broken premise when its plant finds no marked line or never wrote the reader fixture"
problems=()
tree=""
subject_copy=""
run_out=""
run_code=0

# The two ways the plant can fail after the scratch tree is made, each as the one `sed`
# rewrite that causes it, in the repository's `IFS='|' read` table idiom so the name of a
# way and the rewrite that causes it are one row rather than two lists a `case` glob rejoins.
# The first row stops the planted reader from carrying the mark the plant then greps it for,
# which is the fixture edit the issue names; the second stops the reader fixture from being
# written at all, so the grep has no file to read. Both leave every other line of the
# subject as it is, because what is being asked about is the subject, not a rewrite of it.
#
# The first rewrites what `plant_reader` prints rather than the `MARK` constant, and that is
# not a detail: the constant is read twice — once to write the comment and once to find it
# again — so renaming it renames both halves, the grep still matches, and the plant succeeds.
# Both rewrites delimit their `sed` with `%` so the row's own `|` stays the field separator.
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

# probe_plant_is_intact — the premise the case below rests on: the copy standing in the
# scratch tree is the subject byte for byte, so the only thing that differs between the two
# halves is which guard it meets. The rewrite handed to `plant_subject` is a no-op here, and
# a `sed` that silently mangled a line would otherwise leave the half below reporting on a
# subject nobody wrote.
probe_plant_is_intact() {
  cmp -s "$SUBJECT_PATH" "$subject_copy" ||
    problems+=("the copy in the scratch tree is not $SUBJECT_NAME byte for byte, so what it reports is not about the subject")
  return 0
}

# probe_passes_against_the_real_guard — half one, asked of the subject where it stands: run
# in this repository it resolves the real no-docs-reads.test.sh, plants both fixtures, and
# must report its one case as passed. This is the half a fix for #183 could have broken by
# making an intact plant look like a failed one.
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

# probe_fails_against_a_passing_stub — half two, and the half that says the pass above was
# earned rather than vacuous: met by a guard that checks nothing and passes, the same subject
# with the same intact plant must fail. A suite that passed here would be reporting on
# nothing, which is the whole of what #183 is about.
probe_fails_against_a_passing_stub() {
  [[ "$run_code" != 0 ]] ||
    problems+=("against a guard that always passes, $SUBJECT_NAME exited 0 with its plant intact: it is not asking the guard anything. It said: $(flat "$run_out")")
  local count_line
  count_line="$(tail -n 1 <<< "$run_out")"
  [[ "$count_line" == '0 passed, 1 failed' ]] ||
    problems+=("against a guard that always passes, $SUBJECT_NAME did not count its one case as failed; its count line was: $(flat "$count_line")")
}

# 2. One criterion, one case: with the plant intact the subject still discriminates. Both
#    halves are one criterion rather than two — a suite that passes against the real guard
#    and a suite that fails against a stub are each satisfiable by a suite that answers the
#    same way to everything, and only the pair says the answer came from the guard.
#
#    The stub half goes through `plant_subject` with a rewrite that changes nothing: the
#    scratch tree is what puts a different guard in front of the subject, since the subject
#    resolves the guard four directories up from itself.
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

#!/usr/bin/env bash
# Unit tests for the guard suite that keeps the development lane out of the docs tree —
# skills/tdd/scripts/tests/no-docs-reads.test.sh. Like hermetic-suites.test.sh and
# count-line-guard.test.sh this suite has no script as its subject: its subject is what
# another suite reports about the tree it is run in. Zero-dependency plain-shell asserts,
# same idiom as count-line-guard.test.sh.
#
# Why this exists (issue #143): a suite under skills/tdd/scripts/tests/ that opens a file
# under docs/ lets the docs pipeline turn `make test` red — the target preflight reads its
# baseline off, that every Green leaf runs and that both blind verifiers run — over prose
# no development change touched. Deleting today's four sites fixes today; the guard is what
# stops the fifth from being written. But a guard that answers "this suite mentions docs/"
# rather than "this suite reaches into docs/" is worse than none: detect-test-command.test.sh
# seeds `docs/wt/app.js` and `docs/walkthrough.html` into issue bodies as the very text
# #75 mis-parsed (:171, :201), and a guard that refused those would be deleted by the first
# author it blocked, taking the real check with it.
#
# Contract under test:
#   Over a tests directory holding one suite that binds a path under docs/ to a variable and
#   opens it on a later line, and one whose only docs/ path is fixture text it writes into a
#   file of its own, no-docs-reads.test.sh fails, names the reading suite with the line
#   number of the binding, and says nothing about the other.
#
# The reader is planted with the path held in a variable rather than written into the read
# itself, and that is the point of the case rather than a detail of the fixture. It is the
# shape of every site #143 deletes — supervise.test.sh:203 and refactor-budget.test.sh:255
# through a heredoc row, solvable-issues.test.sh:601 and skill-identity.test.sh:189 through
# an assignment, skill-identity.test.sh:175 through a `for` — so a guard that asked each
# line whether it carried both a path and a read verb would pass this repository unchanged
# while catching nothing it was written for. `probe_plant_is_what_it_claims` asserts the
# indirection is real: the planted reader names the tree on exactly one line, and opens the
# file from another.
#
# Both suites are planted rather than asserted about where they stand: after this issue's
# other steps this repository has no suite that reads docs/, so a probe over the real tree
# would pass on both sides of the fix and pin nothing — and one that did read docs/ would
# be the bug rather than the fixture. The plant goes in a scratch tree and the guard is
# copied into it, which is how count-line-guard.test.sh puts a suite in front of the real
# `test` recipe; the guard therefore answers about the planted tree the same way it answers
# about this one, by being run inside it.
#
# No line of code in this file spells that tree's name with its slash — the two paths below
# are built onto `DOCS_DIR`, and the reading line is printf'd into the fixture. That is not
# decoration: a line of THIS suite naming a path in that tree is exactly what the guard
# exists to catch, and a test that trips its own subject on the real tree would make the
# next step unachievable.
#
# Run: skills/tdd/scripts/tests/docs-read-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The guard, twice, and neither name substitutes for the other: repo-relative is what a
# failure message quotes, absolute is what copying it into the plant needs.
GUARD='skills/tdd/scripts/tests/no-docs-reads.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

# Where a suite lives, and so where the plant puts one: the guard is handed a tree, not a
# list, and it has to find both fixtures by the directory they sit in.
TESTS_DIR='skills/tdd/scripts/tests'

# The two planted suites. Named for what each does with a docs/ path rather than for a
# script, because neither has a subject — they exist to be read by the guard, and the
# failure messages below quote their names as the guard would have to.
READER='reads-the-commentary.test.sh'
QUOTER='quotes-a-docs-path.test.sh'

# The tree in question, and the two paths in it the fixtures carry — assembled here rather
# than written out, for the reason the header gives. Real paths: wt/commentary.py is the
# file supervise.test.sh case 10 and refactor-budget.test.sh case 8 open today, and
# wt/app.js is one of the two detect-test-command.test.sh:171 seeds into an issue body as
# prose. A guard that told them apart by name rather than by what the suite does with them
# would pass this case and fail the tree it ships against.
DOCS_DIR='docs'
DOCS_READ_PATH="$DOCS_DIR/wt/commentary.py"
DOCS_FIXTURE_PATH="$DOCS_DIR/wt/app.js"

# The comment the binding line ends in, so this suite can find that line's number without
# searching the fixture for a path of its own — see the header. Nothing about the mark is
# visible to the guard: it is an ordinary trailing comment on an ordinary line of bash.
MARK='the-binding'

# The line the planted reader opens the bound path on, written once because two places must
# spell it identically: `plant` prints it into the fixture, and `probe_plant_is_what_it_claims`
# asserts the read is really there. It reaches the file through `$commentary` and never names
# the tree itself, which is the indirection this whole case exists to pin — a guard matching a
# path beside a read verb finds nothing on this line.
READ_SITE='stated="$(grep -c VERI_HEARTBEAT "$ROOT/$commentary")"'

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

# plant — build the scratch tree the case is asked about and leave its path in `tree`, the
# line number of the binding line in `reader_line`. Both fixtures are whole suites down to
# the count line, because the guard is run over the directory rather than handed a file and
# a directory of half-suites is not the thing it will meet.
#
# The tree is made a git repository with both fixtures staged. Nothing in the contract says
# how the guard enumerates the suites it reads, and `git ls-files` is as reasonable an
# answer as a glob; an unstaged plant would make this case report on that choice instead of
# on the detection it is asking about.
plant() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to plant the two suites in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"

  # The suite the guard must catch: it binds a file in the documentation tree to a variable
  # and opens it four lines later, to read a figure out of the prose. That is the shape of
  # every site this issue deletes — the path and the read verb never share a line.
  cat > "$tree/$TESTS_DIR/$READER" <<'EOF'
#!/usr/bin/env bash
# Unit tests for supervise.sh's heartbeat default — the half of this case that compares the
# code to the page's prose is the shape the guard has to catch.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
pass=0 fail=0
EOF
  printf 'commentary="%s" # %s\n' "$DOCS_READ_PATH" "$MARK" >> "$tree/$TESTS_DIR/$READER"
  printf '%s\n' "$READ_SITE" >> "$tree/$TESTS_DIR/$READER"
  cat >> "$tree/$TESTS_DIR/$READER" <<'EOF'
[[ "$stated" -gt 0 ]] && pass=1 || fail=1
echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
EOF

  # The suite the guard must leave alone: its docs/ path is a string it writes into a file
  # of its own and greps there, never a file it opens in the documentation tree.
  cat > "$tree/$TESTS_DIR/$QUOTER" <<'EOF'
#!/usr/bin/env bash
# Unit tests for detect-test-command.sh — the path here is fixture text handed to the
# subject, the shape the guard must not refuse.
set -uo pipefail
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
EOF
  printf 'echo "## Notes. %s is generated. Test command: make docs-test" > "$work/body.md"\n' \
    "$DOCS_FIXTURE_PATH" >> "$tree/$TESTS_DIR/$QUOTER"
  cat >> "$tree/$TESTS_DIR/$QUOTER" <<'EOF'
grep -q 'make docs-test' "$work/body.md" && pass=1 || fail=1
echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
EOF

  chmod 755 "$tree/$TESTS_DIR/$READER" "$tree/$TESTS_DIR/$QUOTER"
  cp "$GUARD_PATH" "$tree/$TESTS_DIR/$GUARD_NAME"
  git init -q "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1

  reader_line="$(grep -n "$MARK" "$tree/$TESTS_DIR/$READER" | cut -d: -f1)"
}

# probe_guard_is_there — the premise every probe below rests on, and the one that answers
# while the guard does not exist yet: there is a suite at that path and it can be run.
# Returns non-zero so the case stops here rather than reporting a plant it never made.
probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing under $TESTS_DIR is checked for reaching into the documentation tree")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

# probe_plant_is_what_it_claims — the plant's premises, asserted rather than assumed, and
# two of the four are what make this a case about indirection rather than about a literal.
# The binding line has to be findable by its mark and has to really name the path, or
# `reader_line` below is a number the guard was never owed. It has to be the ONLY line of
# the reader naming that tree, and the reader has to open the file through the variable it
# bound — together, those say the guard can have caught the read only by following the
# binding, which is the objection this case exists to pin. The quoter has to really carry
# such a path, or "the guard said nothing about it" is true of a fixture with nothing to
# say about.
probe_plant_is_what_it_claims() {
  [[ "$reader_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted reader has no single marked line to name (found '$reader_line'), so the criterion cannot be asked")
    return
  }
  local marked carriers
  marked="$(sed -n "${reader_line}p" "$tree/$TESTS_DIR/$READER")"
  [[ "$marked" == *"$DOCS_READ_PATH"* ]] ||
    problems+=("the planted reader's line $reader_line does not bind $DOCS_READ_PATH, so there is nothing there to catch: $(flat "$marked")")
  carriers="$(grep -cE "(^|[^[:alnum:]_.-])$DOCS_DIR/" "$tree/$TESTS_DIR/$READER")"
  [[ "$carriers" == 1 ]] ||
    problems+=("the planted reader names the documentation tree on $carriers lines, want exactly 1 — with the path spelled at the read as well, a guard that only matched a path beside a read verb would pass this case")
  grep -qF "$READ_SITE" "$tree/$TESTS_DIR/$READER" ||
    problems+=("the planted reader never opens the file it bound on line $reader_line, so there is no indirect read for the guard to be wrong about")
  grep -q "$DOCS_FIXTURE_PATH" "$tree/$TESTS_DIR/$QUOTER" ||
    problems+=("the planted quoter carries no path in that tree at all, so a guard that refuses fixture text would still pass this case")
}

# probe_guard_names_the_reader_with_its_line — the first half of the criterion, and it asks
# for both halves of what a guard is: a failure, and an address. Not "the output mentions
# the suite" — a guard that listed every suite it read would satisfy that — but a line of
# output that names the reading suite AND carries the line number of the binding, which is
# the only thing that sends the next author to the site rather than to the file.
probe_guard_names_the_reader_with_its_line() {
  guard_out="$("$tree/$TESTS_DIR/$GUARD_NAME" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a suite that binds $DOCS_READ_PATH and opens it on a later line; it exited 0 and said: $(flat "$guard_out")")
  local named
  named="$(grep -F "$READER" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $READER, which reads $DOCS_READ_PATH through the variable bound at line $reader_line; it said: $(flat "$guard_out")")
    return
  }
  grep -qE "(^|[^0-9])$reader_line([^0-9]|\$)" <<< "$named" ||
    problems+=("the guard named $READER but not line $reader_line, where the path enters the suite; the lines naming it were: $(flat "$named")")
}

# probe_guard_leaves_the_quoter_alone — the other half, and the half that keeps the guard
# from being a grep for the tree's name. A suite whose only such path is fixture text it
# writes and reads back is doing nothing this issue forbids, and the guard must have
# nothing to say about it — not a softer complaint, no complaint.
probe_guard_leaves_the_quoter_alone() {
  local named
  named="$(grep -F "$QUOTER" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $QUOTER, whose only such path is the fixture text it writes into a file of its own: $(flat "$named")")
}

# 1. One criterion, one case: the guard tells a read from a mention, follows the read
#    through the variable it is bound to, and says where the binding is. The two halves are
#    probed over one run of the guard against one tree holding both fixtures, because that
#    is the tree it ships against — a guard asked about each shape in isolation could answer
#    "everything here reads that tree" to the first and be caught by nothing.
name="no-docs-reads.test.sh names a suite that binds a path in the documentation tree and opens it later, with the line of the binding, and says nothing about one whose path is only fixture text"
problems=()
tree=""
reader_line=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims
  probe_guard_names_the_reader_with_its_line
  probe_guard_leaves_the_quoter_alone
fi
[[ -z "$tree" ]] || rm -rf "$tree"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

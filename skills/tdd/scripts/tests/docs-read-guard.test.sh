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
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-docs-reads.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

TESTS_DIR='skills/tdd/scripts/tests'

READER='reads-the-commentary.test.sh'
QUOTER='quotes-a-docs-path.test.sh'

DOCS_DIR='docs'
DOCS_READ_PATH="$DOCS_DIR/wt/commentary.py"
DOCS_FIXTURE_PATH="$DOCS_DIR/wt/app.js"

MARK='the-binding'

READ_SITE='stated="$(grep -c VERI_HEARTBEAT "$ROOT/$commentary")"'

pass=0 fail=0

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

flat() { printf '%s' "$1" | tr '\n' '/'; }

plant_reader() {
  cat > "$reader_path" <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
pass=0 fail=0
EOF
  printf 'commentary="%s" # %s\n' "$DOCS_READ_PATH" "$MARK" >> "$reader_path"
  printf '%s\n' "$READ_SITE" >> "$reader_path"
  cat >> "$reader_path" <<'EOF'
[[ "$stated" -gt 0 ]] && pass=1 || fail=1
echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
EOF
  chmod 755 "$reader_path"
}

plant_quoter() {
  cat > "$quoter_path" <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
EOF
  printf 'echo "## Notes. %s is generated. Test command: make docs-test" > "$work/body.md"\n' \
    "$DOCS_FIXTURE_PATH" >> "$quoter_path"
  cat >> "$quoter_path" <<'EOF'
grep -q 'make docs-test' "$work/body.md" && pass=1 || fail=1
echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
EOF
  chmod 755 "$quoter_path"
}

plant() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to plant the two suites in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"

  reader_path="$tree/$TESTS_DIR/$READER"
  quoter_path="$tree/$TESTS_DIR/$QUOTER"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"

  plant_reader
  plant_quoter

  cp "$GUARD_PATH" "$guard_copy"
  git init -q "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1

  reader_line="$(grep -n "$MARK" "$reader_path" | cut -d: -f1)"
  # hazard: without -e, a grep that found no mark would leave plant returning non-zero.
  return 0
}

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

probe_plant_is_what_it_claims() {
  [[ "$reader_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted reader has no single marked line to name (found '$reader_line'), so the criterion cannot be asked")
    return
  }
  local marked carriers
  marked="$(sed -n "${reader_line}p" "$reader_path")"
  [[ "$marked" == *"$DOCS_READ_PATH"* ]] ||
    problems+=("the planted reader's line $reader_line does not bind $DOCS_READ_PATH, so there is nothing there to catch: $(flat "$marked")")
  carriers="$(grep -cE "(^|[^[:alnum:]_.-])$DOCS_DIR/" "$reader_path")"
  [[ "$carriers" == 1 ]] ||
    problems+=("the planted reader names the documentation tree on $carriers lines, want exactly 1 — with the path spelled at the read as well, a guard that only matched a path beside a read verb would pass this case")
  grep -qF "$READ_SITE" "$reader_path" ||
    problems+=("the planted reader never opens the file it bound on line $reader_line, so there is no indirect read for the guard to be wrong about")
  grep -q "$DOCS_FIXTURE_PATH" "$quoter_path" ||
    problems+=("the planted quoter carries no path in that tree at all, so a guard that refuses fixture text would still pass this case")
}

run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

probe_guard_names_the_reader_with_its_line() {
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

probe_guard_leaves_the_quoter_alone() {
  local named
  named="$(grep -F "$QUOTER" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $QUOTER, whose only such path is the fixture text it writes into a file of its own: $(flat "$named")")
}

name="no-docs-reads.test.sh names a suite that binds a path in the documentation tree and opens it later, with the line of the binding, and says nothing about one whose path is only fixture text"
problems=()
tree=""
reader_path=""
quoter_path=""
guard_copy=""
reader_line=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims
  run_guard
  probe_guard_names_the_reader_with_its_line
  probe_guard_leaves_the_quoter_alone
fi
[[ -z "$tree" ]] || rm -rf "$tree"

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

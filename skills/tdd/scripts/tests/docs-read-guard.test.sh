#!/usr/bin/env bash
# Unit tests for skills/tdd/scripts/tests/no-docs-reads.test.sh, the guard that keeps the
# development lane out of the docs tree.
#
# Contract under test:
#   Over a tests directory holding one suite that binds a path under docs/ to a variable and
#   opens it on a later line, and one whose only docs/ path is fixture text it writes into a
#   file of its own, no-docs-reads.test.sh fails, names the reading suite with the line
#   number of the binding, and says nothing about the other.
#
# Run: skills/tdd/scripts/tests/docs-read-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-docs-reads.test.sh'
GUARD_PATH="$ROOT/$GUARD"

TESTS_DIR='skills/tdd/scripts/tests'

READER='reads-the-commentary.test.sh'
QUOTER='quotes-a-docs-path.test.sh'

DOCS_DIR='docs'
DOCS_READ_PATH="$DOCS_DIR/wt/commentary.py"
DOCS_FIXTURE_PATH="$DOCS_DIR/wt/app.js"
UNPLANTED_READ_PATH="fixtures/wt/commentary.py"

MARK='the-binding'

READ_SITE='stated="$(grep -c VERI_HEARTBEAT "$ROOT/$commentary")"'

SKILL="$TESTS_DIR/$READER"


source "$HERE/lib/harness.sh"
source "$HERE/lib/guard-plant.sh"

scratch="$(scratch_dir)"
SKILL_PATH="$scratch/unplanted-$READER"

flat() { printf '%s' "$1" | tr '\n' '/'; }

plant_reader() {
  cat > "$reader_path" <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
pass=0; fail=0
EOF
  printf 'commentary="%s" # %s\n' "$DOCS_READ_PATH" "$MARK" >> "$reader_path"
  printf '%s\n' "$READ_SITE" >> "$reader_path"
  cat >> "$reader_path" <<'EOF'
[[ "$stated" -gt 0 ]] && pass=1 || fail=1
echo "----"
echo "${pass:-0} passed, $fail failed"
[[ "$fail" -eq 0 ]]
EOF
  chmod 755 "$reader_path"
}

plant_quoter() {
  cat > "$quoter_path" <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
work="$(scratch_dir)"
pass=0; fail=0
EOF
  printf 'echo "## Notes. %s is generated. Test command: make docs-test" > "$work/body.md"\n' \
    "$DOCS_FIXTURE_PATH" >> "$quoter_path"
  cat >> "$quoter_path" <<'EOF'
grep -q 'make docs-test' "$work/body.md" && pass=1 || fail=1
echo "----"
echo "${pass:-0} passed, $fail failed"
[[ "$fail" -eq 0 ]]
EOF
  chmod 755 "$quoter_path"
}

plant() {
  reader_path="$scratch/planted-$READER"
  quoter_path="$tree/$TESTS_DIR/$QUOTER"
  planted_skill="$reader_path"

  plant_reader
  plant_quoter
  printf 'test:\n\t@echo $(wildcard %s/*.test.sh)\n' "$TESTS_DIR" > "$tree/Makefile"

  sed "s|$DOCS_READ_PATH|$UNPLANTED_READ_PATH|" "$reader_path" > "$SKILL_PATH" 2>/dev/null
  new_repo "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1

  reader_line="$(grep -n "$MARK" "$reader_path" | cut -d: -f1)"
  # hazard: without -e, a grep that found no mark would leave plant returning non-zero.
  return 0
}

probe_reader_plant_is_what_it_claims() {
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
  run_guard_over "$planted_skill"
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
planted_skill=""
reader_line=""
guard_out=""
guard_code=0

run_plant_sequence tree plant "$UNPLANTED_READ_PATH" "$DOCS_READ_PATH" \
  probe_reader_plant_is_what_it_claims run_guard probe_guard_names_the_reader_with_its_line probe_guard_leaves_the_quoter_alone

report "$name"

finish

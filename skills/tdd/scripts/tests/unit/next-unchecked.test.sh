#!/usr/bin/env bash
# Unit tests for scripts/next-unchecked.sh — the loop/resume primitive. Given a ledger
# (checkbox markdown) on stdin, print the description of the FIRST unchecked `- [ ]` step
# and exit 0; exit 3 when every step is checked (or there are none) — the signal that the
# cycle loop is complete. Mirrors the checkbox grammar of tick-criterion.sh.
#
# Admitted to the fast tier (#336) by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/next-unchecked.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
NEXT="$HERE/../../next-unchecked.sh"
source "$HERE/../lib/harness.sh"
check() {  # check <name> <expected-exit> <input> <expected-stdout>
  local name="$1" exp_code="$2" input="$3" exp="$4" out code
  out="$(printf '%s' "$input" | "$NEXT")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp" ]]; then ok; else
    no "$name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

ledger='# Plan for #42

- [x] add the slugify lowercasing
- [ ] collapse non-alphanumerics to a single hyphen
- [ ] strip leading and trailing hyphens'

check "first unchecked description" 0 "$ledger" "collapse non-alphanumerics to a single hyphen"

done_ledger='- [x] one
- [x] two'
check "all checked exits 3" 3 "$done_ledger" ""

check "no checkboxes exits 3" 3 "# just a heading
some prose" ""

check "nested step" 0 "  - [ ] nested criterion" "nested criterion"

lit='- [x] done one
- [ ] `slugify("a/b")` returns `a-b`'
check "verbatim special chars" 0 "$lit" '`slugify("a/b")` returns `a-b`'

check "first line unchecked" 0 '- [ ] only step' "only step"

owed_ledger='# Plan for #42

- [x] collapse non-alphanumerics to a single hyphen
- [x] strip leading and trailing hyphens

## Owed steps

- a unicode dash collapses too
- an empty slug falls back to "n-a"'
check "owed bullets are not steps" 3 "$owed_ledger" ""

full_suite_ledger='# Plan for #42

- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 1⟧
- [ ] pin the second step ⟦criterion 2⟧'
check "a ⟦full-suite⟧ line is never handed to a leaf (#481)" 0 "$full_suite_ledger" "pin the second step ⟦criterion 2⟧"

human_owed_ledger='# Plan for #42

- [ ] each suite broken on purpose, its red output recorded ⟦human-owed⟧ ⟦criterion 1⟧
- [ ] pin the second step ⟦criterion 2⟧'
check "a ⟦human-owed⟧ line is never handed to a leaf (#481)" 0 "$human_owed_ledger" "pin the second step ⟦criterion 2⟧"

quoting_ledger='# Plan for #42

- [ ] a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 2⟧'
check "a line quoting a marker mid-sentence is handed to a leaf (#484)" 0 "$quoting_ledger" "a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 2⟧"

written_ledger='# Plan for #42

- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 1⟧
- [ ] each suite broken on purpose, its red output recorded ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] pin the third step ⟦criterion 3⟧'
check "a marker in the written position still skips its line (#484)" 0 "$written_ledger" "pin the third step ⟦criterion 3⟧"

both_ledger='# Plan for #42

- [ ] the text quotes ⟦human-owed⟧ yet the suites are green ⟦full-suite⟧ ⟦criterion 1⟧
- [ ] pin the second step ⟦criterion 2⟧'
check "a line with a written marker that also quotes one is skipped (#484)" 0 "$both_ledger" "pin the second step ⟦criterion 2⟧"

ticked_ledger='# Plan for #42

- [x] a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 1⟧
- [x] the suites are green ⟦full-suite⟧ ⟦criterion 2⟧
- [x] pin the third step ⟦criterion 3⟧'
check "a fully ticked ledger quoting markers still exits 3 (#484)" 3 "$ticked_ledger" ""

work="$(scratch_dir)"
mkdir "$work/lib"
cp "$NEXT" "$work/next-unchecked.sh"
cat > "$work/lib/ledger.sh" <<'EOF'
ledger_steps() {
  cat > /dev/null
  printf '1\tdone\tstep\t0\t0\t1\tticked in the module ⟦criterion 1⟧\n'
  printf '2\topen\tfull-suite\t0\t0\t2\tgated in the module ⟦full-suite⟧ ⟦criterion 2⟧\n'
  printf '3\topen\tstep\t0\t0\t3\tasked the module ⟦criterion 3⟧\n'
}
EOF
NEXT="$work/next-unchecked.sh"
check "the first open ordinary step comes from lib/ledger.sh's ledger_steps (#495)" 0 \
  "- [ ] found in the markdown ⟦criterion 1⟧" "asked the module ⟦criterion 3⟧"

finish

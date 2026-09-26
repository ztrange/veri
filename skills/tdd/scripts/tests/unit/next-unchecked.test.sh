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
pass=0 fail=0
check() {  # check <name> <expected-exit> <input> <expected-stdout>
  local name="$1" exp_code="$2" input="$3" exp="$4" out code
  out="$(printf '%s' "$input" | "$NEXT")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp" ]]; then pass=$((pass + 1)); else
    fail=$((fail + 1)); echo "FAIL - $name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

ledger='# Plan for #42

- [x] add the slugify lowercasing
- [ ] collapse non-alphanumerics to a single hyphen
- [ ] strip leading and trailing hyphens'

# 1. returns the description of the first UNCHECKED step, skipping checked ones
check "first unchecked description" 0 "$ledger" "collapse non-alphanumerics to a single hyphen"

# 2. all steps checked → exit 3, no output (loop is done)
done_ledger='- [x] one
- [x] two'
check "all checked exits 3" 3 "$done_ledger" ""

# 3. no checkboxes at all → exit 3
check "no checkboxes exits 3" 3 "# just a heading
some prose" ""

# 4. an indented / nested step is still found
check "nested step" 0 "  - [ ] nested criterion" "nested criterion"

# 5. the description is preserved verbatim, including backticks/special chars
lit='- [x] done one
- [ ] `slugify("a/b")` returns `a-b`'
check "verbatim special chars" 0 "$lit" '`slugify("a/b")` returns `a-b`'

# 6. the very first line being unchecked is returned (no checked lines before it)
check "first line unchecked" 0 '- [ ] only step' "only step"

# 7. a plain bullet under `## Owed steps` is not a step — a ledger whose boxes are all
# ticked still exits 3, never returning an owed text (#360)
owed_ledger='# Plan for #42

- [x] collapse non-alphanumerics to a single hyphen
- [x] strip leading and trailing hyphens

## Owed steps

- a unicode dash collapses too
- an empty slug falls back to "n-a"'
check "owed bullets are not steps" 3 "$owed_ledger" ""

# 8. an unchecked line marked ⟦full-suite⟧ is covered by the run's full-suite gate, not a
# Red/Green step — it is skipped, and the first unchecked line without it is printed (#481)
full_suite_ledger='# Plan for #42

- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 1⟧
- [ ] pin the second step ⟦criterion 2⟧'
check "a ⟦full-suite⟧ line is never handed to a leaf (#481)" 0 "$full_suite_ledger" "pin the second step ⟦criterion 2⟧"

# 9. an unchecked line marked ⟦human-owed⟧ is the record of a manual check, owed by a
# human — it is skipped, and the first unchecked line without it is printed (#481)
human_owed_ledger='# Plan for #42

- [ ] each suite broken on purpose, its red output recorded ⟦human-owed⟧ ⟦criterion 1⟧
- [ ] pin the second step ⟦criterion 2⟧'
check "a ⟦human-owed⟧ line is never handed to a leaf (#481)" 0 "$human_owed_ledger" "pin the second step ⟦criterion 2⟧"

# 10. a line whose text only QUOTES a marker mid-sentence carries none — it is an ordinary
# Red/Green step and is printed, not skipped (#484)
quoting_ledger='# Plan for #42

- [ ] a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 2⟧'
check "a line quoting a marker mid-sentence is handed to a leaf (#484)" 0 "$quoting_ledger" "a step whose text quotes ⟦full-suite⟧ or ⟦human-owed⟧ is still handed to a leaf ⟦criterion 2⟧"

# 11. anchoring the marker keeps the written position working: either marker immediately
# before the closing ⟦criterion k⟧ still skips its line, so the first unmarked step is
# printed (#484)
written_ledger='# Plan for #42

- [ ] the suites are green ⟦full-suite⟧ ⟦criterion 1⟧
- [ ] each suite broken on purpose, its red output recorded ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] pin the third step ⟦criterion 3⟧'
check "a marker in the written position still skips its line (#484)" 0 "$written_ledger" "pin the third step ⟦criterion 3⟧"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

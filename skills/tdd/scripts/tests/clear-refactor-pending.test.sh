#!/usr/bin/env bash
# Tests for scripts/clear-refactor-pending.sh — the in-place removal of the
# ` ⟂ refactor pending` mark tick-ledger.sh --refactor-pending wrote with the green commit.
# Given a ledger file and a matcher, strip the mark from the FIRST checked step that both
# contains the matcher and carries the mark, in place, and exit 0; exit 3 with the file
# byte-identical when no such step matched. Operates on a real temp file.
#
# Run: scripts/tests/clear-refactor-pending.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLEAR="$HERE/../clear-refactor-pending.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

led="$work/issue-42.md"
seed() { printf '# Plan for #42\n\n- [x] add the slugify lowercasing ⟂ refactor pending\n- [x] collapse to single hyphen\n- [x] collapse to single hyphen (again) ⟂ refactor pending\n- [ ] percent-encode the remainder\n' > "$led"; }

# 1. the mark leaves the first matching step that carries it, and only that one; no such
#    step → exit 3 with the file byte-identical
seed
"$CLEAR" "$led" "collapse to single hyphen"; code=$?
cleared="$work/cleared.md"; cp "$led" "$cleared"
"$CLEAR" "$led" "percent-encode the remainder" 2>/dev/null; none_code=$?
{ [[ "$code" == 0 ]] \
  && grep -q '^- \[x\] collapse to single hyphen (again)$' "$cleared" \
  && grep -q '^- \[x\] add the slugify lowercasing ⟂ refactor pending$' "$cleared" \
  && grep -q '^- \[x\] collapse to single hyphen$' "$cleared" \
  && [[ "$none_code" == 3 ]] && cmp -s "$led" "$cleared"; } \
  && ok || no "clears the first matching marked step, else exit 3 and untouched (code=$code none_code=$none_code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

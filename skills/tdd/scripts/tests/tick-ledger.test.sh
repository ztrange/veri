#!/usr/bin/env bash
# Tests for scripts/tick-ledger.sh — the in-place ledger checkbox tick (file wrapper over
# the tested tick-criterion.sh transform). Operates on a real temp file.
#
# Run: scripts/tests/tick-ledger.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TICK="$HERE/../tick-ledger.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work" "$work"' EXIT

led="$work/issue-42.md"
seed() { printf '# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n- [ ] strip edge hyphens\n' > "$led"; }

# 1. ticks the matching step in place, leaves the others unchecked
seed
"$TICK" "$led" "collapse to single hyphen"; code=$?
{ [[ "$code" == 0 ]] \
  && grep -q '^- \[x\] collapse to single hyphen$' "$led" \
  && grep -q '^- \[ \] add lowercasing$' "$led" \
  && grep -q '^- \[ \] strip edge hyphens$' "$led"; } && ok || no "ticks matching step in place (code=$code)"

# 2. no unchecked step matches → exit 3, file unchanged
seed
before="$(cat "$led")"
"$TICK" "$led" "nonexistent step" 2>/dev/null; code=$?
{ [[ "$code" == 3 ]] && [[ "$(cat "$led")" == "$before" ]]; } && ok || no "no match → exit 3, file unchanged (code=$code)"

# 3. an already-checked step is skipped; a later matching unchecked one is ticked
printf -- '- [x] collapse to single hyphen\n- [ ] collapse to single hyphen (again)\n' > "$led"
"$TICK" "$led" "collapse to single hyphen"; code=$?
{ [[ "$code" == 0 ]] && grep -q '^- \[x\] collapse to single hyphen (again)$' "$led"; } \
  && ok || no "skips checked, ticks next matching (code=$code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

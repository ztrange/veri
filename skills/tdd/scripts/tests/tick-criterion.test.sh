#!/usr/bin/env bash
# Unit tests for scripts/tick-criterion.sh — the pure text transform that ticks an
# acceptance-criterion checkbox in an issue body. Zero-dependency plain-shell asserts.
#
# Run: scripts/tests/tick-criterion.test.sh   (exits non-zero if any case fails)
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TICK="$HERE/../tick-criterion.sh"
pass=0 fail=0

# check <name> <expected-exit> <matcher> <input> <expected-output>
# $() strips trailing newlines from both sides, so comparison is clean.
check() {
  local name="$1" exp_code="$2" matcher="$3" input="$4" exp_out="$5"
  local out code
  out="$(printf '%s' "$input" | "$TICK" "$matcher")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp_out" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (matcher=[$matcher] want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

body="## Acceptance criteria

- [ ] reads the issue and creates a branch
- [ ] a start comment is posted
- [ ] a draft PR is opened"

# 1. ticks the first unchecked box matching the substring, leaves others alone
check "ticks matching box" 0 "start comment" "$body" "## Acceptance criteria

- [ ] reads the issue and creates a branch
- [x] a start comment is posted
- [ ] a draft PR is opened"

# 2. flips only the FIRST unchecked box when several match the substring
multi='- [ ] alpha shared
- [ ] beta shared'
check "first match only" 0 "shared" "$multi" '- [x] alpha shared
- [ ] beta shared'

# 3. empty matcher → first unchecked box (slice-1 single-criterion convenience)
check "empty matcher ticks first" 0 "" "$body" "## Acceptance criteria

- [x] reads the issue and creates a branch
- [ ] a start comment is posted
- [ ] a draft PR is opened"

# 4. no unchecked box matches → exit 3, body unchanged
check "no match exits 3" 3 "nonexistent criterion" "$body" "$body"

# 5. matcher treated literally (backticks, slashes, angle brackets, brackets)
lit='- [ ] `/tdd <n>` creates branch `tdd/<n>-slug`
- [ ] other'
check "literal special chars" 0 '`/tdd <n>`' "$lit" '- [x] `/tdd <n>` creates branch `tdd/<n>-slug`
- [ ] other'

# 6. an already-checked box with matching text is skipped; a later unchecked one is ticked
mixed='- [x] reads the issue and creates a branch
- [ ] reads the file and creates a branch'
check "skips already checked" 0 "creates a branch" "$mixed" '- [x] reads the issue and creates a branch
- [x] reads the file and creates a branch'

# 7. indented (nested) checkbox is still tickable
nested='  - [ ] nested criterion'
check "nested checkbox" 0 "nested" "$nested" '  - [x] nested criterion'

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

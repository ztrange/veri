#!/usr/bin/env bash
# Tests for scripts/next-pending-refactor.sh — the resume primitive for a step that is
# green but not yet tidied. Given a ledger (checkbox markdown) on stdin, print the
# description of the FIRST checked step whose line ends in ` ⟂ refactor pending` — without
# that mark, so the description is the substring the refactor loop hands back — and exit 0;
# exit 3 with no output when no step carries it.
#
# Run: scripts/tests/next-pending-refactor.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
NEXT="$HERE/../next-pending-refactor.sh"
pass=0 fail=0
check() {  # check <name> <expected-exit> <input> <expected-stdout>
  local name="$1" exp_code="$2" input="$3" exp="$4" out code
  out="$(printf '%s' "$input" | "$NEXT")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp" ]]; then pass=$((pass + 1)); else
    fail=$((fail + 1)); echo "FAIL - $name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

pending='# Plan for #42

- [x] add the slugify lowercasing
- [x] collapse non-alphanumerics to a single hyphen ⟂ refactor pending
- [x] strip leading and trailing hyphens ⟂ refactor pending
- [ ] percent-encode the remainder'
settled='# Plan for #42

- [x] add the slugify lowercasing
- [ ] collapse non-alphanumerics to a single hyphen'

# 1. the first marked step's description, with the mark stripped
check "first pending description, mark stripped" 0 "$pending" \
  "collapse non-alphanumerics to a single hyphen"

# 2. no step carries the mark → exit 3, no output (nothing to re-enter)
check "no pending step exits 3" 3 "$settled" ""

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

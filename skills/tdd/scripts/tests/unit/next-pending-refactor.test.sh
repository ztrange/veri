#!/usr/bin/env bash
# Tests for scripts/next-pending-refactor.sh — the resume primitive for a step that is
# green but not yet tidied. Given a ledger (checkbox markdown) on stdin, print the
# description of the FIRST checked step whose line ends in ` ⟂ refactor pending` — without
# that mark, so the description is the substring the refactor loop hands back — and exit 0;
# exit 3 with no output when no step carries it.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/next-pending-refactor.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PENDING="$HERE/../../next-pending-refactor.sh"
source "$HERE/../lib/harness.sh"
check() {  # check <name> <expected-exit> <input> <expected-stdout>
  local name="$1" exp_code="$2" input="$3" exp="$4" out code
  out="$(printf '%s' "$input" | "$PENDING")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp" ]]; then ok; else
    no "$name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

pending='# Plan for #42

- [x] add the slugify lowercasing
- [x] collapse non-alphanumerics to a single hyphen ⟂ refactor pending
- [x] strip leading and trailing hyphens ⟂ refactor pending
- [ ] percent-encode the remainder'
check "first pending description, mark stripped" 0 "$pending" \
  "collapse non-alphanumerics to a single hyphen"

settled='# Plan for #42

- [x] add the slugify lowercasing
- [ ] collapse non-alphanumerics to a single hyphen'
check "no pending step exits 3" 3 "$settled" ""

away="$(scratch_dir)"
ln -s "$(cd "$HERE/../../.." && pwd)" "$away/skill"
in_place="$(printf '%s' "$pending" | "$PENDING")" && in_code=0 || in_code=$?
linked="$(cd "$away" && printf '%s' "$pending" | skill/scripts/next-pending-refactor.sh 2>&1)" \
  && link_code=0 || link_code=$?
expect_eq "through a symlink to the skill directory, from another working directory, answers as in place" \
  "0 collapse non-alphanumerics to a single hyphen|$in_code $in_place" "$link_code $linked|$in_code $in_place"

finish

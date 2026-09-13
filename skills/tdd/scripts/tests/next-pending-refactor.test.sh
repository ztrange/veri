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
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# 1. the first marked step's description, mark stripped; no marked step → exit 3, no output
pending='# Plan for #42

- [x] add the slugify lowercasing
- [x] collapse non-alphanumerics to a single hyphen ⟂ refactor pending
- [x] strip leading and trailing hyphens ⟂ refactor pending
- [ ] percent-encode the remainder'
settled='# Plan for #42

- [x] add the slugify lowercasing
- [ ] collapse non-alphanumerics to a single hyphen'

out="$(printf '%s' "$pending" | "$NEXT")"; code=$?
none="$(printf '%s' "$settled" | "$NEXT")"; none_code=$?
{ [[ "$code" == 0 ]] && [[ "$out" == "collapse non-alphanumerics to a single hyphen" ]] \
  && [[ "$none_code" == 3 ]] && [[ -z "$none" ]]; } \
  && ok || no "first pending step without the mark, else exit 3 (code=$code out='$out' none_code=$none_code none='$none')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

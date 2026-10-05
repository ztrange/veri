#!/usr/bin/env bash
# Unit tests for scripts/next-unchecked.sh — the loop/resume primitive. Given a ledger
# (checkbox markdown) on stdin, print the description of the FIRST unchecked `- [ ]` step
# and exit 0; exit 3 when every step is checked (or there are none) — the signal that the
# cycle loop is complete. Mirrors the checkbox grammar of tick-criterion.sh.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
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

linked="$(scratch_dir)"
ln -s "$(cd "$HERE/../../.." && pwd)" "$linked/skill"
mkdir "$linked/elsewhere"
name="run through a symlink to the skill directory from another directory, answers as in place"
want="collapse non-alphanumerics to a single hyphen"
got="$(cd "$linked/elsewhere" && printf '%s' "$ledger" | ../skill/scripts/next-unchecked.sh)" && code=0 || code=$?
if [[ "$code" == 0 && "$got" == "$want" ]]; then ok; else
  no "$name (want exit 0, got $code)"
  diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
fi

finish

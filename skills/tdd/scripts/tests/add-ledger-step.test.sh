#!/usr/bin/env bash
# Tests for scripts/add-ledger-step.sh — inserts a step, marked ⟦added⟧, next to an anchor
# step already in the plan. Operates on a real temp file.
#
# Run: scripts/tests/add-ledger-step.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ADD="$HERE/../add-ledger-step.sh"
source "$HERE/lib/harness.sh"

check_code() {
  local name="$1" code="$2" want_code="$3" want="$4" got
  got="$(cat "$led")"
  if [[ "$code" == "$want_code" && "$got" == "$want" ]]; then
    ok
  else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$want") <(printf '%s\n' "$got") | sed 's/^/    /'
  fi
}

check() { check_code "$1" "$2" 0 "$3"; }

work="$(scratch_dir)"

led="$work/issue-42.md"

seeded='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse to single hyphen ⟦criterion 2⟧
- [ ] strip edge hyphens ⟦criterion 3⟧'

seed() { printf '%s\n' "$seeded" > "$led"; }

finish

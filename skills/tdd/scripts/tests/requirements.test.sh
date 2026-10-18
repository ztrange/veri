#!/usr/bin/env bash
# Tests for scripts/requirements.sh — reads a REQUIREMENTS.md: `units <file>` prints each prose
# unit the file declares, one per line, in file order.
#
# Run: scripts/tests/requirements.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REQUIREMENTS="$HERE/../requirements.sh"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

cat > "$work/REQUIREMENTS.md" <<'MD'
# Requirements

## skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

## skills/tdd/SKILL.md#Phase two

| ID | Requirement | Why |
|----|-------------|-----|
| B1 | Says another. | Since. |

## docs/guide.md

| ID | Requirement | Why |
|----|-------------|-----|
| C1 | Says a third. | Hence. |
MD

out="$("$REQUIREMENTS" units "$work/REQUIREMENTS.md" 2> "$work/stderr")" && code=0 || code=$?
expect_eq "units prints each declared prose unit, one per line, in file order" \
  $'0\nskills/tdd/SKILL.md\nskills/tdd/SKILL.md#Phase two\ndocs/guide.md' "$code"$'\n'"$out"

finish

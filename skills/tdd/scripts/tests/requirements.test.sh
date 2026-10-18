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
H='##'

cat > "$work/REQUIREMENTS.md" <<MD
${H:0:1} Requirements

$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

$H skills/tdd/SKILL.md#Phase two

| ID | Requirement | Why |
|----|-------------|-----|
| B1 | Says another. | Since. |

$H guide/unit.md

| ID | Requirement | Why |
|----|-------------|-----|
| C1 | Says a third. | Hence. |
MD

out="$("$REQUIREMENTS" units "$work/REQUIREMENTS.md" 2> "$work/stderr")" && code=0 || code=$?
expect_eq "units prints each declared prose unit, one per line, in file order" \
  $'0\nskills/tdd/SKILL.md\nskills/tdd/SKILL.md#Phase two\nguide/unit.md' "$code"$'\n'"$out"

cat > "$work/two-rows.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because secret-one. |
| A2 | Says two things. | Since secret-two. |
MD

out="$("$REQUIREMENTS" claims "$work/two-rows.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
expect_eq "claims prints a unit's rows as ID<TAB>Requirement in table order, with no Why text" \
  $'0\nA1\tSays one thing.\nA2\tSays two things.' "$code"$'\n'"$out"

cat > "$work/dup-id.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |
| A1 | Says it again. | Since. |
MD

out="$("$REQUIREMENTS" claims "$work/dup-id.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])6([^0-9]|$) ]] && named=yes
expect_eq "claims on a repeated ID exits 2, prints nothing on stdout and names the duplicate row's line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/empty-req.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |
| A2 |  | Since. |
MD

out="$("$REQUIREMENTS" claims "$work/empty-req.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])6([^0-9]|$) ]] && named=yes
expect_eq "claims on a row with an empty Requirement exits 2, prints nothing on stdout and names that row's line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/empty-id.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |
|  | Says another. | Since. |
MD

out="$("$REQUIREMENTS" claims "$work/empty-id.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])6([^0-9]|$) ]] && named=yes
expect_eq "claims on a row with an empty ID exits 2, prints nothing on stdout and names that row's line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/no-why.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement |
|----|-------------|
| A1 | Says one thing. |
MD

out="$("$REQUIREMENTS" claims "$work/no-why.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])3([^0-9]|$) ]] && named=yes
expect_eq "claims on a table header lacking a column exits 2, prints nothing on stdout and names the header's line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

out="$("$REQUIREMENTS" claims "$work/absent.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"
says=no; [[ "$err" == *missing* && "$err" == *"$work/absent.md"* ]] && says=yes
expect_eq "claims on a file that does not exist exits 2, prints nothing on stdout and says on stderr the file is missing, naming it" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$says"

out="$("$REQUIREMENTS" claims "$work/two-rows.md" skills/tdd/NOPE.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"
says=no; [[ "$err" == *"not declared"* && "$err" == *skills/tdd/NOPE.md* ]] && says=yes
expect_eq "claims on a unit the file does not declare exits 2, prints nothing on stdout and says on stderr the unit is not declared, naming it" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$says"

finish

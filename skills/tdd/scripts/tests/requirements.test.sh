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

cat > "$work/no-id-column.md" <<MD
$H skills/tdd/SKILL.md

| Key | Requirement | Why |
|-----|-------------|-----|
| A1 | Says one thing. | Because. |
MD

out="$("$REQUIREMENTS" claims "$work/no-id-column.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])3([^0-9]|$) ]] && named=yes
expect_eq "claims on a table header lacking the ID column exits 2, prints nothing on stdout and names the header's line on stderr" \
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

cat > "$work/no-requirement-column.md" <<MD
$H skills/tdd/SKILL.md

| ID | Why |
|----|-----|
| A1 | Because. |
MD

out="$("$REQUIREMENTS" claims "$work/no-requirement-column.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])3([^0-9]|$) ]] && named=yes
expect_eq "claims on a table header lacking the Requirement column exits 2, prints nothing on stdout and names the header's line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/swapped-columns.md" <<MD
$H skills/tdd/SKILL.md

| Requirement | ID |
|-------------|----|
| Do it. | A1 |
MD

out="$("$REQUIREMENTS" claims "$work/swapped-columns.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])3([^0-9]|$) ]] && named=yes
expect_eq "claims on a table header of | Requirement | ID | exits 2, prints nothing on stdout and names the header's line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

uout="$("$REQUIREMENTS" units "$work/swapped-columns.md" 2> /dev/null)" && ucode=0 || ucode=$?
out="$("$REQUIREMENTS" claims "$work/swapped-columns.md" skills/tdd/SKILL.md 2> /dev/null)" && code=0 || code=$?
expect_eq "units does not print a heading whose only table is | Requirement | ID | and claims refuses it (#1743)" \
  $'0\n\n2\n' "$ucode"$'\n'"$uout"$'\n'"$code"$'\n'"$out"

cat > "$work/pipeless.md" <<MD
$H skills/tdd/SKILL.md

ID | Requirement | Why
---|-------------|----
A1 | Do it. | Because.
MD

out="$("$REQUIREMENTS" claims "$work/pipeless.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])3([^0-9]|$) ]] && named=yes
expect_eq "claims on a table without leading pipes exits 2, prints nothing on stdout and names the header's line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/no-table.md" <<MD
$H skills/tdd/SKILL.md

Nothing is claimed here yet.
MD

out="$("$REQUIREMENTS" claims "$work/no-table.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])1([^0-9]|$) ]] && named=yes
expect_eq "claims on a heading with prose and no table exits 2, prints nothing on stdout and names the heading's line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/second-table.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Do it. | Because. |

| ID | Requirement | Why |
|----|-------------|-----|
| A2 | Do more. | Because. |
MD

out="$("$REQUIREMENTS" claims "$work/second-table.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])7([^0-9]|$) ]] && named=yes
expect_eq "claims on a unit with a second table exits 2, prints nothing on stdout and names the second header's line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/later-key-table.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Do it. | Because. |

| Key | Requirement |
MD

out="$("$REQUIREMENTS" claims "$work/later-key-table.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])7([^0-9]|$) ]] && named=yes
expect_eq "claims on a unit with a later | Key | Requirement | line exits 2, prints nothing on stdout and names that line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/escaped-pipe.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Pipes a \| b. | Why. |
MD

out="$("$REQUIREMENTS" claims "$work/escaped-pipe.md" skills/tdd/SKILL.md 2> /dev/null)" && code=0 || code=$?
expect_eq "claims keeps an escaped pipe inside a requirement cell (#1743)" \
  $'0\nA1\tPipes a \\| b.' "$code"$'\n'"$out"

out="$("$REQUIREMENTS" units "$work/absent.md" 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"
shape=bad; [[ "$err" != *$'\n'* && "$err" == *"$work/absent.md"* && "$err" != *Traceback* ]] && shape=ok
expect_eq "units on a missing file exits 2 with one stderr line naming the file and no traceback (#1743)" \
  $'2\n\nok' "$code"$'\n'"$out"$'\n'"$shape"

out="$("$REQUIREMENTS" 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"
usage=no; [[ "$err" == usage:*requirements.sh* ]] && usage=yes
expect_eq "requirements.sh with no arguments exits 2, prints nothing on stdout and its usage line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$usage"

finish

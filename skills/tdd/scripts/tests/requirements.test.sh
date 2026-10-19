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
cat > "$work/later-table-line.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |
Afterwards:
| A | B |
MD

out="$("$REQUIREMENTS" claims "$work/later-table-line.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])7([^0-9]|$) ]] && named=yes
expect_eq "claims on a unit with a later | A | B | line after its table exits 2, prints nothing on stdout and names that line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/second-table.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

| ID | Requirement | Why |
|----|-------------|-----|
| B1 | Says another. | Because. |
MD

out="$("$REQUIREMENTS" claims "$work/second-table.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])7([^0-9]|$) ]] && named=yes
expect_eq "claims on a unit with a second | ID | Requirement | Why | table after a blank line exits 2, prints nothing on stdout and names the second header's line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/fenced-pipe.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

\`\`\`
ls | grep x
\`\`\`
MD

out="$("$REQUIREMENTS" claims "$work/fenced-pipe.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
expect_eq "claims on a unit with a fenced code block holding ls | grep x after its table exits 0 and prints only the table's rows (#1743)" \
  $'0\nA1\tSays one thing.' "$code"$'\n'"${out%$'\n'}"

cat > "$work/fenced-table-line.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

\`\`\`
| A | B |
\`\`\`
MD

out="$("$REQUIREMENTS" claims "$work/fenced-table-line.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
expect_eq "claims on a unit with a fenced code block holding a | A | B | line after its table exits 0 and prints only the table's rows (#1743)" \
  $'0\nA1\tSays one thing.' "$code"$'\n'"${out%$'\n'}"

cat > "$work/fence-ends-table.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |
\`\`\`
code
\`\`\`
| X | Y |
MD

out="$("$REQUIREMENTS" claims "$work/fence-ends-table.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])9([^0-9]|$) ]] && named=yes
expect_eq "claims on a unit whose table rows run straight into a fence, then a | X | Y | line after it, exits 2, prints nothing on stdout and names that line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/prose-pipe.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

a | b
MD

out="$("$REQUIREMENTS" claims "$work/prose-pipe.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
expect_eq "claims on a unit with a prose a | b line after its table exits 0 and prints only the table's rows (#1743)" \
  $'0\nA1\tSays one thing.' "$code"$'\n'"${out%$'\n'}"

cat > "$work/no-pipes.md" <<MD
${H:0:1} Requirements

$H skills/tdd/SKILL.md

Key | Value
----|------
A1  | Says one thing.
MD

out="$("$REQUIREMENTS" claims "$work/no-pipes.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"; err="${err//"$work"/}"
named=no; [[ "$err" =~ (^|[^0-9])3([^0-9]|$) ]] && named=yes
expect_eq "claims on a heading whose only table is Key | Value without leading pipes exits 2, prints nothing on stdout and names the heading line on stderr (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$named"

cat > "$work/escaped-pipe.md" <<MD
$H skills/tdd/SKILL.md

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says a \| b in full. | Because. |
MD

out="$("$REQUIREMENTS" claims "$work/escaped-pipe.md" skills/tdd/SKILL.md 2> "$work/stderr")" && code=0 || code=$?
expect_eq "claims on a requirement holding an escaped \\| prints the whole requirement with the pipe (#1743)" \
  $'0\nA1\tSays a \\| b in full.' "$code"$'\n'"${out%$'\n'}"

out="$("$REQUIREMENTS" units "$work/absent.md" 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"
shape=no; [[ "$err" == *"$work/absent.md"* && "$err" != *$'\n'* && "$err" != *Traceback* ]] && shape=yes
expect_eq "units on a missing file exits 2, prints nothing on stdout and one stderr line naming the file with no traceback (#1743)" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$shape"

cat > "$work/one-parser.md" <<MD
${H:0:1} Requirements

$H valid

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

$H no-why

| Requirement | ID |
|-------------|----|
| Says one thing. | A1 |

$H why-id

| Why | ID |
|-----|----|
| Because. | A1 |

$H key-requirement

| Key | Requirement |
|-----|-------------|
| A1 | Says one thing. |

$H key-value

| Key | Value |
|-----|-------|
| A1 | Says one thing. |

$H extra-column

| ID | Requirement | Why | Extra |
|----|-------------|-----|-------|
| A1 | Says one thing. | Because. | More. |

$H no-leading-pipes

Key | Value
----|------
A1  | Says one thing.

$H prose-only

Only prose, no table here.

$H later-line

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

prose between

| A | B |

$H second-table

| ID | Requirement | Why |
|----|-------------|-----|
| A1 | Says one thing. | Because. |

| ID | Requirement | Why |
|----|-------------|-----|
| B1 | Says another. | Since. |
MD

units_out="$("$REQUIREMENTS" units "$work/one-parser.md" 2> "$work/stderr")"
accepted=""
while IFS= read -r heading; do
  "$REQUIREMENTS" claims "$work/one-parser.md" "$heading" > /dev/null 2>&1 && accepted+="$heading"$'\n'
done < <(grep '^## ' "$work/one-parser.md" | cut -c4-)
expect_eq "units prints exactly the headings for which claims exits 0, over a valid unit and every malformed shape (#1743)" \
  $'valid\nvalid' "$units_out"$'\n'"${accepted%$'\n'}"

out="$("$REQUIREMENTS" 2> "$work/stderr")" && code=0 || code=$?
err="$(< "$work/stderr")"
usage=no; [[ "$err" == usage:*requirements.sh* ]] && usage=yes
expect_eq "requirements.sh with no arguments exits 2, prints nothing on stdout and its usage line on stderr" \
  $'2\n\nyes' "$code"$'\n'"$out"$'\n'"$usage"

finish

#!/usr/bin/env bash
# add-ledger-step.sh <ledger-file> after <anchor-substring> <text> — grow the plan while a
# run is under way (issue #360).
#
# Inserts <text> as an unchecked step `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` on the line after
# the step containing <anchor-substring>. The added step inherits the anchor's criterion, so
# criterion-finished.sh keeps counting it against the same acceptance criterion; the ⟦added⟧
# mark goes first because that reader takes the criterion from the line's end.
#
# Usage:   add-ledger-step.sh .tdd/issue-<n>.md after 'collapse to single hyphen' 'a unicode dash too'
set -euo pipefail

file="${1:?usage: add-ledger-step.sh <ledger-file> after <anchor-substring> <text>}"
where="${2:?missing after}"
anchor="${3:?missing <anchor-substring>}"
text="${4:?missing <text>}"

# criterion_of <step-line> -> ` ⟦criterion k⟧`, or nothing when the line carries none.
# Read with globs rather than a regex: the marks are multibyte and suites run under LC_ALL=C.
criterion_of() {
  local line="$1" k
  [[ "$line" == *"⟦criterion "*"⟧"* ]] || return 0
  k="${line##*⟦criterion }"
  printf ' ⟦criterion %s⟧' "${k%%⟧*}"
}

out=""
while IFS= read -r line; do
  out+="$line"$'\n'
  if [[ "$where" == after && "$line" == *"$anchor"* ]]; then
    out+="- [ ] $text ⟦added⟧$(criterion_of "$line")"$'\n'
  fi
done < "$file"

printf '%s' "$out" > "$file"

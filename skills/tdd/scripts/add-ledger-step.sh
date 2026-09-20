#!/usr/bin/env bash
# add-ledger-step.sh <ledger-file> after|before <anchor-substring> <text> [<text> …] — grow
# the plan while a run is under way (issue #360).
#
# Inserts each <text> as an unchecked step `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` on the lines
# after the step containing <anchor-substring>, or on the lines before it, in the order
# given. VERI_STEP_GROWTH (default 3) caps how many ⟦added⟧ steps one ledger may hold, and
# the call is all or nothing: a batch that would exceed the cap inserts nothing, exits 1 and
# records every text as a plain bullet under `## Owed steps`, where next-unchecked.sh will
# not find it. The added step inherits the anchor's criterion, so criterion-finished.sh keeps
# counting it against the same acceptance criterion; the ⟦added⟧ mark goes first because that
# reader takes the criterion from the line's end.
#
# Usage:   add-ledger-step.sh .tdd/issue-<n>.md after 'collapse to single hyphen' 'a unicode dash too'
set -euo pipefail

usage='usage: add-ledger-step.sh <ledger-file> after|before <anchor-substring> <text> [<text> …]'
file="${1:?$usage}"
where="${2:?$usage}"
anchor="${3:?$usage}"
[[ $# -ge 4 ]] || { printf '%s\n' "$usage" >&2; exit 2; }
shift 3
texts=("$@")

# criterion_of <step-line> -> ` ⟦criterion k⟧`, or nothing when the line carries none.
# Read with globs rather than a regex: the marks are multibyte and suites run under LC_ALL=C.
criterion_of() {
  local line="$1" k
  [[ "$line" == *"⟦criterion "*"⟧"* ]] || return 0
  k="${line##*⟦criterion }"
  printf ' ⟦criterion %s⟧' "${k%%⟧*}"
}

# added_steps <anchor-line> -> one `- [ ] …` line per text, in the order given.
added_steps() {
  local line="$1" crit text
  crit="$(criterion_of "$line")"
  for text in "${texts[@]}"; do
    printf '%s\n' "- [ ] $text ⟦added⟧$crit"
  done
}

budget="${VERI_STEP_GROWTH:-3}"

# added_held -> how many ⟦added⟧ steps the ledger already holds.
added_held() {
  local line n=0
  while IFS= read -r line; do
    if [[ "$line" == *"⟦added⟧"* ]]; then n=$((n + 1)); fi
  done < "$file"
  printf '%s' "$n"
}

if (( $(added_held) + ${#texts[@]} > budget )); then
  {
    printf '\n## Owed steps\n\n'
    for text in "${texts[@]}"; do printf -- '- %s\n' "$text"; done
  } >> "$file"
  exit 1
fi

out=""
while IFS= read -r line; do
  if [[ "$line" == *"$anchor"* ]]; then
    steps="$(added_steps "$line")"
    if [[ "$where" == before ]]; then line="$steps"$'\n'"$line"; fi
    if [[ "$where" == after ]]; then line="$line"$'\n'"$steps"; fi
  fi
  out+="$line"$'\n'
done < "$file"

printf '%s' "$out" > "$file"

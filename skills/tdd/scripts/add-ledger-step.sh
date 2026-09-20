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

# The mark an added step carries, named once: `added_steps` writes it and `is_added_step`
# counts it against the budget, so the two must spell it the same way. Other ledger readers
# name their mark the same way — clear-refactor-pending.sh's `mark`, criterion-finished.sh's
# `tag`.
added='⟦added⟧'

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
    printf '%s\n' "- [ ] $text $added$crit"
  done
}

# is_anchor_step <line> — the line is a step (`- [ ]` or `- [x]`) holding the anchor
# substring; is_added_step <line> — the line is one an earlier call added.
is_anchor_step() { [[ "$1" == "- ["*"]"* && "$1" == *"$anchor"* ]]; }
is_added_step() { [[ "$1" == *"$added"* ]]; }

# count_lines <predicate> -> how many of the ledger's lines the named predicate accepts.
count_lines() {
  local pred="$1" line n=0
  while IFS= read -r line; do
    if "$pred" "$line"; then n=$((n + 1)); fi
  done < "$file"
  printf '%s' "$n"
}

# The anchor has to name one step and no other: none means the plan has moved on, more than
# one means the caller cannot have known where the step would land, and both are refusals
# rather than a guess.
[[ "$(count_lines is_anchor_step)" == 1 ]] || {
  printf 'add-ledger-step.sh: anchor matches no single step: %s\n' "$anchor" >&2
  exit 2
}

# Unset means three. Set-but-empty is read with `-` rather than `:-` so it reaches the guard
# as the empty string instead of silently falling back to the default: a budget that is not a
# whole number >= 0 is a refusal, like an anchor that names no single step.
budget="${VERI_STEP_GROWTH-3}"

if [[ ! "$budget" =~ ^[0-9]+$ ]]; then
  printf 'add-ledger-step.sh: VERI_STEP_GROWTH must be a whole number >= 0: %s\n' "$budget" >&2
  exit 2
fi

if (( $(count_lines is_added_step) + ${#texts[@]} > budget )); then
  {
    printf '\n## Owed steps\n\n'
    for text in "${texts[@]}"; do printf -- '- %s\n' "$text"; done
  } >> "$file"
  exit 1
fi

out=""
while IFS= read -r line; do
  if is_anchor_step "$line"; then
    steps="$(added_steps "$line")"
    case "$where" in
      before) line="$steps"$'\n'"$line" ;;
      after) line="$line"$'\n'"$steps" ;;
    esac
  fi
  out+="$line"$'\n'
done < "$file"

printf '%s' "$out" > "$file"

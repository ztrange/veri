#!/usr/bin/env bash
# add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]
# — grow the plan while a run is under way (issue #360).
#
# Inserts each <text> as an unchecked step `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` on the lines
# after the step containing <anchor-substring>, or on the lines before it, in the order
# given. `instead-of` puts them where that step was and drops the step itself — the
# placement a step that turned out to be several behaviours takes (issue #408).
# VERI_STEP_GROWTH (default 3) caps how many ⟦added⟧ steps one ledger may hold, and
# the call is all or nothing: a batch that would exceed the cap inserts nothing, exits 1 and
# records every text as a plain bullet under `## Owed steps`, where next-unchecked.sh will
# not find it. The added step inherits the anchor's criterion, so criterion-finished.sh keeps
# counting it against the same acceptance criterion; the ⟦added⟧ mark goes first because that
# reader takes the criterion from the line's end.
#
# Usage:   add-ledger-step.sh .tdd/issue-<n>.md after 'collapse to single hyphen' 'a unicode dash too'
set -euo pipefail

usage='usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]'
[[ $# -ge 4 && -n "$1" && -n "$2" && -n "$3" ]] || { printf '%s\n' "$usage" >&2; exit 2; }
file="$1"
where="$2"
anchor="$3"
shift 3
texts=("$@")

added='⟦added⟧'

# hazard: the marks are multibyte, and under LC_ALL=C a regex reads them byte by byte.
criterion_of() {
  local line="$1" k
  [[ "$line" == *"⟦criterion "*"⟧"* ]] || return 0
  k="${line##*⟦criterion }"
  printf ' ⟦criterion %s⟧' "${k%%⟧*}"
}

added_steps() {
  local line="$1" crit text
  crit="$(criterion_of "$line")"
  for text in "${texts[@]}"; do
    printf '%s\n' "- [ ] $text $added$crit"
  done
}

is_anchor_step() { [[ "$1" == "- ["*"]"* && "$1" == *"$anchor"* ]]; }
is_added_step() { [[ "$1" == *"$added"* ]]; }

count_lines() {
  local pred="$1" line n=0
  while IFS= read -r line; do
    if "$pred" "$line"; then n=$((n + 1)); fi
  done < "$file"
  printf '%s' "$n"
}

[[ "$(count_lines is_anchor_step)" == 1 ]] || {
  printf 'add-ledger-step.sh: anchor matches no single step: %s\n' "$anchor" >&2
  exit 2
}

# hazard: `-`, not `:-`, so set-but-empty reaches the guard rather than the default.
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
      instead-of) line="$steps" ;;
    esac
  fi
  out+="$line"$'\n'
done < "$file"

printf '%s' "$out" > "$file"

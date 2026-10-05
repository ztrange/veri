#!/usr/bin/env bash
# add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]
# — grow the plan while a run is under way.
#
# Inserts each <text> as an unchecked step `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` on the lines
# after the step containing <anchor-substring>, or on the lines before it, in the order
# given. `instead-of` puts them where that step was and drops the step itself — the
# placement a step that turned out to be several behaviours takes.
# VERI_STEP_GROWTH (default 5) caps how many ⟦added⟧ steps one ledger may hold, and
# the call is all or nothing: a batch that would exceed the cap inserts nothing, exits 1 and
# records every text as a plain bullet under `## Owed steps`, where next-unchecked.sh will
# not find it. A <text> carrying ⟦ci-repair⟧ or ⟦suite-repair⟧ is inserted without ⟦added⟧
# and never counts against the cap. The added step inherits the anchor's criterion, so criterion-finished.sh keeps
# counting it against the same acceptance criterion; the ⟦added⟧ mark goes first because that
# reader takes the criterion from the line's end.
#
# Usage:   add-ledger-step.sh .tdd/issue-<n>.md after 'collapse to single hyphen' 'a unicode dash too'
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/lib/ledger.sh"
source "$HERE/lib/exit-contract.sh"

USAGE='usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]'
(( $# >= 4 )) || refuse
require_args 3 "$@"
file="$1"
where="$2"
anchor="$3"
shift 3
texts=("$@")

place() {
  case "$where" in
    before) placed="$1"$'\n'"$2" ;;
    after) placed="$2"$'\n'"$1" ;;
    instead-of) placed="$1" ;;
    *) return 1 ;;
  esac
}

place '' '' || {
  printf 'add-ledger-step.sh: position must be after, before or instead-of: %s\n' "$where" >&2
  exit 2
}

ci_repair='⟦ci-repair⟧'
suite_repair='⟦suite-repair⟧'

# hazard: the marks are multibyte, and under LC_ALL=C a regex reads them byte by byte.
criterion_of() {
  local line="$1" k
  [[ "$line" == *"$_ledger_criterion_tag"*"⟧"* ]] || return 0
  k="${line##*"$_ledger_criterion_tag"}"
  printf '%s' "${k%%⟧*}"
}

added_steps() {
  local line="$1" k crit text step
  k="$(criterion_of "$line")"
  crit="${k:+ $_ledger_criterion_tag$k⟧}"
  for text in "${texts[@]}"; do
    step="$(ledger_add_step "$text" "$k" < /dev/null)"
    printf '%s\n' "${step% "$_ledger_added_mark $_ledger_criterion_tag$k⟧"}$(added_mark "$text")$crit"
  done
}

is_step() { [[ -n "$(ledger_steps <<< "$1")" ]]; }
is_anchor_step() { [[ "$1" == *"$anchor"* ]] && is_step "$1"; }
is_added_step() { _ledger_is_added "$1" && is_step "$1"; }
is_repair() { [[ "$1" == *"$ci_repair"* || "$1" == *"$suite_repair"* ]]; }
added_mark() { is_repair "$1" || printf ' %s' "$_ledger_added_mark"; }

count_lines() {
  local pred="$1" line n=0
  while IFS= read -r line; do
    if "$pred" "$line"; then n=$((n + 1)); fi
  done < "$file"
  printf '%s' "$n"
}

last_heading() {
  local line heading=""
  while IFS= read -r line; do
    if [[ "$line" == '## '* ]]; then heading="$line"; fi
  done < "$file"
  printf '%s' "$heading"
}

[[ "$(count_lines is_anchor_step)" == 1 ]] || {
  printf 'add-ledger-step.sh: anchor matches no single step: %s\n' "$anchor" >&2
  exit 2
}

# hazard: `-`, not `:-`, so set-but-empty reaches the guard rather than the default.
budget="${VERI_STEP_GROWTH-5}"

if [[ ! "$budget" =~ ^[0-9]+$ ]]; then
  printf 'add-ledger-step.sh: VERI_STEP_GROWTH must be a whole number >= 0: %s\n' "$budget" >&2
  exit 2
fi

growth=0
for text in "${texts[@]}"; do
  if ! is_repair "$text"; then growth=$((growth + 1)); fi
done

if (( $(count_lines is_added_step) + growth > budget )); then
  {
    [[ "$(last_heading)" == '## Owed steps' ]] || printf '\n## Owed steps\n\n'
    for text in "${texts[@]}"; do printf -- '- %s\n' "$text"; done
  } >> "$file"
  exit 1
fi

out=""
while IFS= read -r line; do
  if is_anchor_step "$line"; then
    steps="$(added_steps "$line")"
    place "$steps" "$line"
    line="$placed"
  fi
  out+="$line"$'\n'
done < "$file"

printf '%s' "$out" > "$file"

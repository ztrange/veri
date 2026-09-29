#!/usr/bin/env bash
# Unit tests for scripts/lib/ledger.sh — the ledger's grammar, sourced, not run. The suite
# sources the module and calls its functions in-process, the seam its callers share.
#
# Contract under test:
#   ledger_steps — stdin → one tab-separated record per step line, in document order:
#   index  state  kind  pending  added  criterion  text. `index` is 1-based over step lines
#   only; `state` is `open` for `[ ]` and `done` for `[x]` or `[X]`; `text` is last.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/ledger.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/ledger.sh"
pass=0 fail=0

verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
}

expect_records() {
  if [[ "$3" != "$2" ]]; then
    problems+="    $1 (want, then got):"$'\n'
    problems+="$(diff <(printf '%s\n' "$2") <(printf '%s\n' "$3") | sed 's/^/    /')"$'\n'
  fi
}

records_of() {
  printf '%s' "$2" | (source "$LIB" && ledger_steps) 2>&1 | awk -F '\t' "{ print $1 }"
}

steps_of() {
  records_of '$1 "\t" $2 "\t" $NF' "$1"
}

# 1. index, state and text: one record per step line at any indent, index counting step lines
#    only, `[x]` and `[X]` both done, and headings, prose and `## Owed steps` bullets skipped.
problems=""
if [[ ! -f "$LIB" ]]; then
  problems+="    want $LIB to exist"$'\n'
else
  if ! sed -n 2p "$LIB" | grep -F 'sourced, not run' > /dev/null; then
    problems+="    want the header's second line to say 'sourced, not run', got: $(sed -n 2p "$LIB")"$'\n'
  fi
  if grep -F 'BASH_SOURCE[0]' "$LIB" > /dev/null; then
    problems+="    want no main guard, found: $(grep -nF 'BASH_SOURCE[0]' "$LIB")"$'\n'
  fi
fi
doc='# Plan for #42

Some prose about the plan.
- [x] lowercase the slug
  - [ ] collapse non-alphanumerics to one hyphen
- [X] strip leading hyphens

## Owed steps

- a bullet with no box
'
want=$'1\tdone\tlowercase the slug\n2\topen\tcollapse non-alphanumerics to one hyphen\n3\tdone\tstrip leading hyphens'
expect_records "ledger_steps index/state/text differ" "$want" "$(steps_of "$doc")"
verdict "ledger_steps prints index, state and text per step line at any indent, skipping lines with no box"

# 2. a final step line with no trailing newline still yields its record.
problems=""
want=$'1\tdone\tfirst\n2\topen\tlast step'
expect_records "ledger_steps records differ for an unterminated last line" "$want" \
  "$(steps_of $'- [x] first\n- [ ] last step')"
verdict "ledger_steps emits a record for a final step line with no trailing newline"

# 3. kind: the marker counts only when it sits immediately before the criterion tag.
problems=""
doc='- [ ] plain step ⟦criterion 1⟧
- [ ] the whole suite is green ⟦full-suite⟧ ⟦criterion 2⟧
- [ ] a person checks the page ⟦human-owed⟧ ⟦criterion 3⟧
- [ ] mentions ⟦full-suite⟧ in passing ⟦criterion 4⟧
'
want=$'1\tstep\n2\tfull-suite\n3\thuman-owed\n4\tstep'
expect_records "ledger_steps kind differs" "$want" \
  "$(records_of '$1 "\t" $3' "$doc")"
verdict "ledger_steps kind is full-suite or human-owed only for a marker right before the criterion tag, step otherwise"

# 4. pending: 1 only for a ticked step ending in the refactor-pending mark, which leaves its text.
problems=""
doc='- [x] tidied ⟦criterion 1⟧
- [x] green ⟦criterion 2⟧ ⟂ refactor pending
- [ ] open ⟦criterion 3⟧
- [ ] open but marked ⟦criterion 4⟧ ⟂ refactor pending
'
want=$'1\t0\ttidied ⟦criterion 1⟧\n2\t1\tgreen ⟦criterion 2⟧\n3\t0\topen ⟦criterion 3⟧\n4\t0\topen but marked ⟦criterion 4⟧ ⟂ refactor pending'
expect_records "ledger_steps pending differs" "$want" \
  "$(records_of '$1 "\t" $4 "\t" $NF' "$doc")"
verdict "ledger_steps pending is 1 for a ticked step ending in the pending mark, 0 otherwise, and the mark leaves its text"

# 5. added and criterion: `⟦added⟧` sets added, `⟦criterion k⟧` gives k, no tag gives empty.
problems=""
doc='- [x] planned ⟦criterion 1⟧
- [ ] discovered ⟦added⟧ ⟦criterion 12⟧
- [ ] untagged
'
want=$'1\t0\t1\n2\t1\t12\n3\t0\t'
expect_records "ledger_steps added/criterion differ" "$want" \
  "$(records_of '$1 "\t" $5 "\t" $6' "$doc")"
verdict "ledger_steps added is 1 for a step carrying the added mark and criterion is its k, empty with no tag"

# 6. ledger_tick: the first open step containing the matcher (empty: the first open step)
#    becomes `- [x]`; prose and ticked lines that match are passed over, every other byte kept.
problems=""
tick_of() {
  local doc="$1" status
  shift
  printf '%s' "$doc" | (source "$LIB" && ledger_tick "$@") 2>&1
  status=$?
  printf '.'
  return "$status"
}
doc='# Plan for the slug

Prose about the slug.
- [x] lowercase the slug ⟦criterion 1⟧
- [ ] trim whitespace ⟦criterion 2⟧
  - [ ] collapse the slug ⟦criterion 3⟧
- [ ] strip the slug ⟦criterion 4⟧'
want="${doc/  - \[ \] collapse/  - [x] collapse}."
expect_records "ledger_tick 'slug' output differs" "$want" "$(tick_of "$doc" 'slug')"
want="${doc/- \[ \] trim/- [x] trim}."
expect_records "ledger_tick '' output differs" "$want" "$(tick_of "$doc" '')"
verdict "ledger_tick ticks the first open step containing the matcher, or the first open step for an empty one, changing no other byte"

# 7. ledger_tick <matcher> pending: the ticked line also gains the refactor-pending mark.
problems=""
doc='- [x] lowercase the slug ⟦criterion 1⟧
- [ ] trim whitespace ⟦criterion 2⟧
- [ ] strip the slug ⟦criterion 3⟧
'
want="${doc/- \[ \] strip the slug ⟦criterion 3⟧/- [x] strip the slug ⟦criterion 3⟧ ⟂ refactor pending}."
expect_records "ledger_tick 'strip' pending output differs" "$want" "$(tick_of "$doc" 'strip' pending)"
verdict "ledger_tick <matcher> pending ticks the step and appends the refactor-pending mark in the same write"

# 8. ledger_tick with no open step containing the matcher: exit 3, the document unchanged,
#    even where prose and a ticked step contain it.
problems=""
doc='# Plan for the slug

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] trim whitespace ⟦criterion 2⟧
'
got="$(tick_of "$doc" 'slug')"
expect_records "ledger_tick exit status differs" "3" "$?"
expect_records "ledger_tick 'slug' output differs" "$doc." "$got"
verdict "ledger_tick returns 3 and writes the document unchanged when no open step contains the matcher"

# 9. ledger_clear_pending: the first ticked step containing the matcher and carrying the mark
#    loses it; prose, an unmarked ticked step and an open marked step are passed over. With no
#    such step: exit 3, the document unchanged.
problems=""
clear_of() {
  local doc="$1" status
  shift
  printf '%s' "$doc" | (source "$LIB" && ledger_clear_pending "$@") 2>&1
  status=$?
  printf '.'
  return "$status"
}
doc='# Plan for the slug ⟂ refactor pending

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] trim the slug ⟦criterion 2⟧ ⟂ refactor pending
  - [x] collapse the slug ⟦criterion 3⟧ ⟂ refactor pending
- [x] strip the slug ⟦criterion 4⟧ ⟂ refactor pending'
want="${doc/collapse the slug ⟦criterion 3⟧ ⟂ refactor pending/collapse the slug ⟦criterion 3⟧}."
got="$(clear_of "$doc" 'slug')"
expect_records "ledger_clear_pending 'slug' exit status differs" "0" "$?"
expect_records "ledger_clear_pending 'slug' output differs" "$want" "$got"
got="$(clear_of "$doc" 'lowercase')"
expect_records "ledger_clear_pending 'lowercase' exit status differs" "3" "$?"
expect_records "ledger_clear_pending 'lowercase' output differs" "$doc." "$got"
verdict "ledger_clear_pending strips the pending mark from the first marked ticked step containing the matcher, changing no other byte, and returns 3 with the document unchanged when none does"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

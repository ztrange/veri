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

steps_of() {
  printf '%s' "$1" | (source "$LIB" && ledger_steps) 2>&1 |
    awk -F '\t' '{ print $1 "\t" $2 "\t" $NF }'
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

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]

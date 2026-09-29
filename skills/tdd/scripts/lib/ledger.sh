#!/usr/bin/env bash
# lib/ledger.sh — sourced, not run: defines `ledger_steps`.
#
# ledger_steps — stdin → one tab-separated record per step line, in document order:
# index  state  kind  pending  added  criterion  text. `index` is 1-based over step lines only; `state` is `open` for
# `[ ]` and `done` for `[x]` or `[X]`; `kind` is `full-suite` or `human-owed` when that marker
# sits immediately before the step's `⟦criterion k⟧`, `step` otherwise; `pending` is `1` for a
# `done` step whose line ends in ` ⟂ refactor pending`, which is then cut from `text`, and `0`
# otherwise; `added` is `1` for a step carrying `⟦added⟧`, `0` otherwise; `criterion` is the `k` of
# its `⟦criterion k⟧`, empty when it carries none. A line with no box is skipped.
ledger_steps() {
  local line state kind pending added criterion text index=0
  local mark=' ⟂ refactor pending'
  local re='^[[:space:]]*- \[([ xX])\] (.*)$'
  local criterion_re='⟦criterion ([0-9]+)⟧'
  local kind_re="⟦(full-suite|human-owed)⟧ $criterion_re"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ $re ]] || continue
    index=$((index + 1))
    state=done
    [[ "${BASH_REMATCH[1]}" == " " ]] && state=open
    text="${BASH_REMATCH[2]}"
    kind=step
    [[ "$text" =~ $kind_re ]] && kind="${BASH_REMATCH[1]}"
    added=0
    [[ "$text" == *'⟦added⟧'* ]] && added=1
    criterion=
    [[ "$text" =~ $criterion_re ]] && criterion="${BASH_REMATCH[1]}"
    pending=0
    if [[ "$state" == done && "$text" == *"$mark" ]]; then
      pending=1
      text="${text%"$mark"}"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$index" "$state" "$kind" "$pending" "$added" "$criterion" "$text"
  done
}

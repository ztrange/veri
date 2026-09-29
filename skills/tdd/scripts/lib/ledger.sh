#!/usr/bin/env bash
# lib/ledger.sh — sourced, not run: defines `ledger_steps`.
#
# ledger_steps — stdin → one tab-separated record per step line, in document order:
# index  state  text. `index` is 1-based over step lines only; `state` is `open` for `[ ]`
# and `done` for `[x]` or `[X]`. A line with no box is skipped.
ledger_steps() {
  local line state index=0
  local re='^[[:space:]]*- \[([ xX])\] (.*)$'
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ $re ]] || continue
    index=$((index + 1))
    state=done
    [[ "${BASH_REMATCH[1]}" == " " ]] && state=open
    printf '%s\t%s\t%s\n' "$index" "$state" "${BASH_REMATCH[2]}"
  done
}

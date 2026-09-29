#!/usr/bin/env bash
# lib/ledger.sh — sourced, not run: defines `ledger_steps`, `ledger_tick`, `ledger_clear_pending` and
# `ledger_add_step`.
#
# ledger_steps — stdin → one tab-separated record per step line, in document order:
# index  state  kind  pending  added  criterion  text. `index` is 1-based over step lines only; `state` is `open` for
# `[ ]` and `done` for `[x]` or `[X]`; `kind` is `full-suite` or `human-owed` when that marker
# sits immediately before the step's `⟦criterion k⟧`, `step` otherwise; `pending` is `1` for a
# `done` step whose line ends in ` ⟂ refactor pending`, which is then cut from `text`, and `0`
# otherwise; `added` is `1` for a step carrying `⟦added⟧`, `0` otherwise; `criterion` is the `k` of
# its `⟦criterion k⟧`, empty when it carries none. A line with no box is skipped.
#
# ledger_tick <matcher> [pending] — stdin → stdout: the first open step whose line contains <matcher>
# (an empty matcher: the first open step) becomes `[x]`, and with `pending` also gains
# ` ⟂ refactor pending` at its end; every other byte is copied unchanged.
# Exit: 0 a step was ticked; 3 no open step contains <matcher>.
#
# ledger_clear_pending <matcher> — stdin → stdout: the first done step whose line contains <matcher>
# and ends in ` ⟂ refactor pending` loses that mark; every other byte is copied unchanged.
# Exit: 0 a mark was cleared; 3 no such step.
#
# ledger_add_step <text> <k> — stdin → stdout: `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` is written
# directly after the last step line; every other byte is copied unchanged.
# Assigns the caller's locals `re`, `open_step` and `done_box`: bash scopes a callee's assignment dynamically.
_ledger_step_re() {
  re='^([[:space:]]*-[[:space:]])\[([ xX])\]( (.*))?$' open_step='- [ ]' done_box='[x]'
}

_ledger_read_line() {
  if IFS= read -r line; then
    nl=$'\n'
  else
    nl=
    [[ -n "$line" ]]
  fi
}

_ledger_pending_mark=' ⟂ refactor pending'
_ledger_added_mark='⟦added⟧'

ledger_steps() {
  local line state kind pending added criterion text index=0 re open_step done_box
  _ledger_step_re
  local criterion_re='⟦criterion ([0-9]+)⟧'
  local kind_re="⟦(full-suite|human-owed)⟧ $criterion_re"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" =~ $re ]] || continue
    index=$((index + 1))
    state=done
    [[ "${BASH_REMATCH[2]}" == " " ]] && state=open
    text="${BASH_REMATCH[4]}"
    kind=step
    [[ "$text" =~ $kind_re ]] && kind="${BASH_REMATCH[1]}"
    added=0
    [[ "$text" == *"$_ledger_added_mark"* ]] && added=1
    criterion=
    [[ "$text" =~ $criterion_re ]] && criterion="${BASH_REMATCH[1]}"
    pending=0
    if [[ "$state" == done && "$text" == *"$_ledger_pending_mark" ]]; then
      pending=1
      text="${text%"$_ledger_pending_mark"}"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$index" "$state" "$kind" "$pending" "$added" "$criterion" "$text"
  done
}

ledger_tick() {
  local matcher="$1" suffix= line nl ticked=0 re open_step done_box
  [[ "${2:-}" == pending ]] && suffix="$_ledger_pending_mark"
  _ledger_step_re
  while _ledger_read_line; do
    if ((ticked == 0)) && [[ "$line" =~ $re && "${BASH_REMATCH[2]}" == " " && "$line" == *"$matcher"* ]]; then
      line="${BASH_REMATCH[1]}$done_box${BASH_REMATCH[3]}$suffix"
      ticked=1
    fi
    printf '%s%s' "$line" "$nl"
  done
  ((ticked)) || return 3
}

ledger_clear_pending() {
  local matcher="$1" line nl cleared=0 re open_step done_box
  _ledger_step_re
  while _ledger_read_line; do
    if ((cleared == 0)) && [[ "$line" =~ $re && "${BASH_REMATCH[2]}" != " " && "$line" == *"$matcher"* && "$line" == *"$_ledger_pending_mark" ]]; then
      line="${line%"$_ledger_pending_mark"}"
      cleared=1
    fi
    printf '%s%s' "$line" "$nl"
  done
  ((cleared)) || return 3
}

ledger_add_step() {
  local step line nl re open_step done_box i last=-1
  local -a lines=() nls=()
  _ledger_step_re
  step="$open_step $1 $_ledger_added_mark ⟦criterion $2⟧"
  while _ledger_read_line; do
    [[ "$line" =~ $re ]] && last=${#lines[@]}
    lines+=("$line")
    nls+=("$nl")
  done
  for i in "${!lines[@]}"; do
    if ((i == last)); then
      printf '%s\n%s%s' "${lines[i]}" "$step" "${nls[i]}"
    else
      printf '%s%s' "${lines[i]}" "${nls[i]}"
    fi
  done
}

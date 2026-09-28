#!/usr/bin/env bash
# lib/background.sh — sourced, not run: defines `bg_start` and `bg_kill`.
#
# bg_start <record> <cmd> [args…] — run <cmd> in the background, append its pid and command
# to <record>, and arm an EXIT trap that names on stderr every recorded process still running.
# bg_kill <record> — kill every process <record> names; one already gone is not an error.
#
# hazard: `$!` is read at once, since a later one is another background command's pid.
_bg_records=()

_bg_report_survivors() {
  local record pid cmd
  for record in ${_bg_records+"${_bg_records[@]}"}; do
    [[ -r "$record" ]] || continue
    while read -r pid cmd; do
      if kill -0 "$pid" 2>/dev/null; then
        printf 'background process still running at exit: pid %s started by %s (kill it: kill %s)\n' \
          "$pid" "$cmd" "$pid" >&2
      fi
    done < "$record"
  done
}

bg_start() {
  local record="${1:?usage: bg_start <record> <cmd> [args...]}"
  shift
  "$@" &
  printf '%s %s\n' "$!" "$*" >> "$record"
  _bg_remember "$record"
}

_bg_remember() {
  local known
  for known in ${_bg_records+"${_bg_records[@]}"}; do
    [[ "$known" == "$1" ]] && return 0
  done
  _bg_records+=("$1")
  # hazard: a subshell's `trap -p` prints its parent's traps until it sets one; untrappable KILL clears them.
  trap - KILL
  eval "set -- $(trap -p EXIT)"
  trap "${3:+$3$'\n'}_bg_report_survivors" EXIT
}

bg_kill() {
  local record="${1:?usage: bg_kill <record>}" pid
  while read -r pid _; do
    kill "$pid" 2>/dev/null || true
  done < "$record"
}

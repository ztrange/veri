#!/usr/bin/env bash
# lib/exit-contract.sh — sourced, not run: defines `refuse` and `require_args`.
#
# refuse [message] — print <message> (if given), then the caller's $USAGE, on stderr; exit 2.
# require_args <n> "$@" — refuse unless the first <n> arguments are present and non-empty;
#   return 0 otherwise.
refuse() {
  if (( $# > 0 )); then
    printf '%s\n' "$1" >&2
  fi
  printf '%s\n' "$USAGE" >&2
  exit 2
}

require_args() {
  local n="$1" i
  shift
  for (( i = 1; i <= n; i++ )); do
    [[ -n "${!i:-}" ]] || refuse
  done
  return 0
}

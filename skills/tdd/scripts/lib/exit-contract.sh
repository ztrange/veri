#!/usr/bin/env bash
# lib/exit-contract.sh — sourced, not run: defines `refuse`.
#
# refuse [message] — print <message> (if given), then the caller's $USAGE, on stderr; exit 2.
refuse() {
  if (( $# > 0 )); then
    printf '%s\n' "$1" >&2
  fi
  printf '%s\n' "$USAGE" >&2
  exit 2
}

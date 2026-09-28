#!/usr/bin/env bash
# comment-class.sh — print every `#` line of the given shell files as `<file>:<line>:<class>`.
#
# Usage: comment-class.sh <file>…
#
# Class 1 is a comment in code, 3 a `#` line inside a heredoc.
#
# Exit: 0 printed, 2 bad arguments.
set -uo pipefail

if (( $# == 0 )); then
  echo "usage: comment-class.sh <file>…" >&2
  exit 2
fi

awk '
  FNR == 1 { delim = "" }
  delim != "" {
    if ($0 == delim) delim = ""
    else if ($0 ~ /^[[:space:]]*#/) print FILENAME ":" FNR ":3"
    next
  }
  /^[[:space:]]*#/ { print FILENAME ":" FNR ":1"; next }
  match($0, /<<[[:space:]]*[A-Za-z_][A-Za-z0-9_]*/) {
    delim = substr($0, RSTART + 2, RLENGTH - 2)
    sub(/^[[:space:]]+/, "", delim)
  }
' "$@"
